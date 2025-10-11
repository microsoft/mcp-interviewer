"""File read/write tool with line numbers and size protection."""

import re
from pathlib import Path

from openai.types.responses import FunctionToolParam

from ..config import AgentConfig


class FileTool:
    """Tool for reading and writing files with size limits."""

    def __init__(self, config: AgentConfig):
        """Initialize the file tool.

        Args:
            config: Agent configuration with output limits
        """
        self.max_chars = config.max_file_read_chars
        self.read_files: set[str] = set()  # Track which files have been read

    @staticmethod
    def get_readlines_tool_definition() -> FunctionToolParam:
        """Get the readlines tool definition for the LLM."""
        return {
            "type": "function",
            "name": "readlines",
            "description": "Read a file with line numbers prepended. For large files, use offset and limit parameters to read specific sections.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read",
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Line number to start from (1-indexed, optional)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of lines to read (optional)",
                    },
                },
                "required": ["path"],
            },
            "strict": None,
        }

    @staticmethod
    def get_findlines_tool_definition() -> FunctionToolParam:
        """Get the findlines tool definition for the LLM."""
        return {
            "type": "function",
            "name": "findlines",
            "description": "Search for lines matching a regex pattern in a file. Returns line numbers and content of matching lines. Use offset/limit to paginate through many results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to search",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Regex pattern to search for (e.g., '# TOOLS', 'def.*tool', 'class \\w+')",
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Skip this many matches before returning results (default: 0)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of matches to return (default: all matches)",
                    },
                },
                "required": ["path", "pattern"],
            },
            "strict": None,
        }

    @staticmethod
    def get_writelines_tool_definition() -> FunctionToolParam:
        """Get the writelines tool definition for the LLM."""
        return {
            "type": "function",
            "name": "writelines",
            "description": "Write content to a file. Can either overwrite the entire file, or replace a specific line range. Do not include line numbers in the content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file",
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Starting line number (1-indexed, inclusive) for replacement. If provided with end_line, only this line range will be replaced.",
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "Ending line number (1-indexed, inclusive) for replacement. If provided with start_line, lines from start_line to end_line will be deleted and replaced with content.",
                    },
                },
                "required": ["path", "content"],
            },
            "strict": None,
        }

    def readlines(
        self, path: str, offset: int | None = None, limit: int | None = None
    ) -> str:
        """Read a file with line numbers prepended.

        Args:
            path: Path to file
            offset: Start reading from this line number (1-indexed)
            limit: Maximum number of lines to read

        Returns:
            File content with line numbers: "1\\tline\\n2\\tline\\n...",
            or error message if too large
        """
        try:
            file_path = Path(path)

            if not file_path.exists():
                return f"Error: File '{path}' does not exist"

            if not file_path.is_file():
                return f"Error: '{path}' is not a file"

            # Read all lines
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            total_lines = len(lines)

            # If offset/limit specified, slice the lines
            if offset is not None or limit is not None:
                # Validate offset
                if offset is not None and offset > total_lines:
                    return (
                        f"Error: offset ({offset}) exceeds file length ({total_lines} lines). "
                        f"File '{path}' has {total_lines} lines. Use offset <= {total_lines}."
                    )

                start = (offset - 1) if offset else 0
                end = (start + limit) if limit else None
                lines_to_output = lines[start:end]
                line_start = start + 1

                # Check if we got any lines
                if not lines_to_output:
                    return (
                        f"Error: No lines in requested range. File '{path}' has {total_lines} lines, "
                        f"but requested starting from line {offset}."
                    )
            else:
                # Check size first if no offset/limit
                full_content = "".join(
                    f"{i + 1}\t{line}" for i, line in enumerate(lines)
                )
                if len(full_content) > self.max_chars:
                    return (
                        f"Error: File '{path}' is too large "
                        f"({len(full_content)} chars, {total_lines} lines > "
                        f"{self.max_chars} limit). Use offset and limit parameters "
                        f"to read specific sections. For example: "
                        f"file_read('{path}', offset=1, limit=100) to read lines 1-100."
                    )
                return full_content

            # Format with line numbers
            result = "".join(
                f"{line_start + i}\t{line}" for i, line in enumerate(lines_to_output)
            )

            # Mark file as read
            self.read_files.add(str(file_path.resolve()))

            return result

        except UnicodeDecodeError:
            return (
                f"Error: File '{path}' appears to be binary and cannot be read as text"
            )
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def writelines(
        self,
        path: str,
        content: str,
        start_line: int | None = None,
        end_line: int | None = None,
    ) -> str:
        """Write content to a file (overwrites existing or replaces line range).

        Args:
            path: Path to file
            content: Raw content to write (no line numbers)
            start_line: Starting line number (1-indexed, inclusive) for replacement
            end_line: Ending line number (1-indexed, inclusive) for replacement

        Returns:
            Success message or error if content too large
        """
        try:
            # Check content size
            if len(content) > self.max_chars:
                return (
                    f"Error: Content to write is too large "
                    f"({len(content)} chars > {self.max_chars} limit). "
                    f"Consider breaking into multiple files or reducing content size."
                )

            file_path = Path(path)
            file_path_resolved = str(file_path.resolve())

            # Check if file exists and hasn't been read yet
            if file_path.exists() and file_path_resolved not in self.read_files:
                return (
                    f"Error: Cannot write to '{path}' - file has not been read yet. "
                    f"You must read the file first using readlines or findlines before modifying it. "
                    f"This ensures you understand the current file structure before making changes."
                )

            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Handle line range replacement
            if start_line is not None and end_line is not None:
                # Read existing file
                if not file_path.exists():
                    return f"Error: Cannot replace line range in non-existent file '{path}'"

                with open(file_path, encoding="utf-8") as f:
                    lines = f.readlines()

                total_lines = len(lines)

                # Validate line range
                if start_line < 1 or end_line < 1:
                    return f"Error: Line numbers must be >= 1 (got start={start_line}, end={end_line})"
                if start_line > end_line:
                    return f"Error: start_line ({start_line}) must be <= end_line ({end_line})"
                if start_line > total_lines:
                    return f"Error: start_line ({start_line}) exceeds file length ({total_lines} lines)"

                # Convert to 0-indexed
                start_idx = start_line - 1
                end_idx = min(end_line, total_lines)  # end_line is inclusive

                # Ensure content ends with newline if we're inserting in the middle
                if not content.endswith("\n") and end_idx < total_lines:
                    content = content + "\n"

                # Build new file content
                new_lines = lines[:start_idx] + [content] + lines[end_idx:]
                final_content = "".join(new_lines)

                # Write the modified content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(final_content)

                # Mark file as read (since we just read it for the replacement)
                self.read_files.add(file_path_resolved)

                lines_deleted = end_idx - start_idx
                new_line_count = content.count("\n") + (
                    0 if content.endswith("\n") else 1
                )
                return f"Successfully replaced lines {start_line}-{end_line} ({lines_deleted} lines deleted, {new_line_count} lines inserted) in '{path}'"

            # Full file write (no line range specified) - NOT ALLOWED
            else:
                return (
                    f"Error: Full file overwrite is not allowed with writelines. "
                    f"You must use start_line and end_line parameters to replace specific sections. "
                    f"If you need to completely rewrite the file, use bash_command with a heredoc or redirection. "
                    f"Example: bash_command('cat > {path} << \\'EOF\\'\\n...\\nEOF') "
                    f"or better yet, use findlines to locate the section you want to modify, "
                    f"then use writelines with start_line and end_line to replace just that section."
                )

        except Exception as e:
            return f"Error writing file: {str(e)}"

    def findlines(
        self,
        path: str,
        pattern: str,
        offset: int | None = None,
        limit: int | None = None,
    ) -> str:
        """Search for lines matching a regex pattern in a file.

        Args:
            path: Path to file
            pattern: Regex pattern to search for
            offset: Skip this many matches before returning results
            limit: Maximum number of matches to return

        Returns:
            Line numbers and content of matching lines, or error message
        """
        try:
            file_path = Path(path)

            if not file_path.exists():
                return f"Error: File '{path}' does not exist"

            if not file_path.is_file():
                return f"Error: '{path}' is not a file"

            # Compile regex pattern
            try:
                regex = re.compile(pattern)
            except re.error as e:
                return f"Error: Invalid regex pattern '{pattern}': {e}"

            # Read file and search
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            # Find matching lines
            all_matches = []
            for i, line in enumerate(lines, start=1):
                if regex.search(line):
                    all_matches.append(f"{i}\t{line.rstrip()}")

            # Mark file as read
            self.read_files.add(str(file_path.resolve()))

            if not all_matches:
                return f"No matches found for pattern '{pattern}' in '{path}'"

            total_matches = len(all_matches)

            # Apply offset and limit
            start_idx = offset if offset else 0
            if start_idx >= total_matches:
                return (
                    f"Error: offset ({start_idx}) >= total matches ({total_matches}). "
                    f"Found {total_matches} matches, but offset skips all of them."
                )

            end_idx = (start_idx + limit) if limit else None
            matches = all_matches[start_idx:end_idx]
            shown_count = len(matches)

            # Build result
            result = "\n".join(matches)

            # Build summary message
            if offset or limit:
                remaining = total_matches - start_idx - shown_count
                summary = f"Found {total_matches} total matches (showing {shown_count}"
                if offset:
                    summary += f", skipped first {start_idx}"
                if remaining > 0:
                    summary += f", {remaining} more available"
                summary += "):\n"
            else:
                summary = f"Found {total_matches} matches:\n"

            return summary + result

        except UnicodeDecodeError:
            return (
                f"Error: File '{path}' appears to be binary and cannot be read as text"
            )
        except Exception as e:
            return f"Error searching file: {str(e)}"
