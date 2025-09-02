# Contributing

This project welcomes contributions and suggestions. Most contributions require you to
agree to a Contributor License Agreement (CLA) declaring that you have the right to,
and actually do, grant us the rights to use your contribution. For details, visit
https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need
to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the
instructions provided by the bot. You will only need to do this once across all repositories using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Installation

```bash
git clone git@github.com:microsoft/mcp-interviewer.git
cd mcp-interviewer

uv venv
uv sync --all-extras --all-groups

pre-commit install
```

Before committing (or if precommit gives you ruff errors), you can format the code and fix any fixable errors (e.g. import sorting) via:

```bash
uv run poe fix
```

## Project Structure

### Constraints

#### Contributing New Constraints

To add new constraint validation rules, create a new class in `src/mcp_interviewer/constraints/`:

1. Inherit from `Constraint` base class
2. Implement required classmethods: `cli_name()` and `cli_code()`
3. Implement the `test()` method that yields `ConstraintViolation` instances
4. Set appropriate severity levels (WARNING or CRITICAL)

Constraints can be selected via the CLI using either their full name or shorthand code.

### Statistics

#### Contributing New Statistics

To add new statistics to the MCP Interviewer, create new classes in `src/mcp_interviewer/statistics/`:

1. Inherit from `Statistic` base class (or `FunctionalTestStepStatistic` for test-specific stats)
2. Implement the `compute()` method that yields `StatisticValue` instances
3. Focus on data analysis and calculation logic
4. Return structured data that report classes can format for display
5. Let the report classes handle formatting and presentation

Statistics modules are responsible for data computation and aggregation, while report classes handle the visual formatting and markdown generation.

### Reports

#### Contributing New Reports

To add new report sections, create a new class in `src/mcp_interviewer/reports/`:

1. Inherit from `BaseReport`
2. Implement required classmethods: `cli_name()` and `cli_code()` 
3. Use the report building utilities (`add_title()`, `add_text()`, `start_collapsible()`, etc.)
4. Reports are responsible for formatting and presentation, not data computation

Reports can be included in custom report compositions via the `--reports` CLI flag using either their full name or shorthand code.
