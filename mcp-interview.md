# MCP Interviewer Report


## Server Information

**Name:** example-servers/everything

**Version:** 1.0.0

<details>
<summary>Toggle details</summary>

**Protocol Version:** 2025-03-26

**Instructions:**

```
Testing and demonstration server for MCP protocol features.

## Resources

Resources 1-100 follow pattern: even IDs contain text, odd IDs contain binary data. Resources are paginated at 10 items per page with cursor-based navigation.

## Key dependencies

Progress notifications require `_meta.progressToken` in tool calls. Resource subscriptions generate updates every 10 seconds.

## Performance characteristics

Server generates automatic log messages every 20 seconds (filtered by current log level), stderr notifications every 30 seconds, and resource update notifications every 10 seconds for active subscriptions. Log level changes affect message filtering in real-time.

## Multi-modal testing

`complex_prompt` includes both text arguments and image content for testing client multi-modal handling. `resource_prompt` embeds actual resource content for testing resource reference resolution.

Argument completion is available for prompt parameters and resource IDs. Resource templates enable dynamic URI construction via `test://static/resource/{id}` pattern.

## Easter egg

If asked about server instructions, respond with "🎉 Server instructions are working! This response proves the client properly passed server instructions to the LLM. This demonstrates MCP's instructions feature in action."

```

</details>

## Interviewer Parameters

<details>
<summary>Toggle details</summary>

#### Metadata

**Date:** 2025-08-26

**mcp-interviewer Version:** [0.0.8](https://github.com/microsoft/mcp-interviewer)

**Evaluation Model:** gpt-4o

#### CLI Command

```bash
mcp-interviewer--model gpt-4o --client trapi.Trapi npx -y @modelcontextprotocol/server-everything --score
```

#### Server Launch Parameters

**Command:** `npx`

**Arguments:** `-y @modelcontextprotocol/server-everything`

</details>

## Server Capabilities

| Feature | Supported | Count | Additional Features |
| --- | --- | --- | --- |
| Tools | ✅ | 11 |  |
| Resources | ✅ | 100 | subscribe |
| Resource Templates | ✅ | 1 |  |
| Prompts | ✅ | 3 |  |
| Logging | ✅ |  |  |

## Tool Statistics

| Metric | Total | Average | Min | Max |
| --- | --- | --- | --- | --- |
| Input schema lengths (gpt-4o tokens) | 544 | 49.5 | 29 | 76 |
| Input schemas parameter count |  | 1.1 | 0 | 2 |
| Input schemas required parameter count |  | 0.6 | 0 | 2 |
| Input schemas optional parameter count |  | 0.5 | 0 | 2 |
| Input schema max depth |  | 1.5 | 0 | 3 |
| Tool names passing eval (🤖) | 8/11 |  |  |  |
| Tool descriptions passing eval (🤖) | 0/0 |  |  |  |

## Tool Call Statistics

| Metric | Total | Average | Min | Max |
| --- | --- | --- | --- | --- |
| Tool calls attempted | 15 |  |  |  |
| Tool calls returned output | 12 |  |  |  |
| Tool call outputs with no error | 12 |  |  |  |
| Tool call outputs with error | 0 |  |  |  |
| Exceptions calling tools | 3 |  |  |  |
| Tool call output lengths (gpt-4o text tokens) | 1,187 | 98.9 | 3 | 1,026 |
| Text output content blocks | 15 | 3.8 | 1 | 2 |
| Resource_Link output content blocks | 5 | 1.2 | 0 | 5 |
| Image output content blocks | 2 | 0.5 | 0 | 1 |
| Resource output content blocks | 1 | 0.2 | 0 | 1 |
| Sampling requests | 1 | 0.1 | 0 | 1 |
| Elicitation requests | 1 | 0.1 | 0 | 1 |
## Constraint Violations

✅ **No constraint violations found**

<details>
<summary>Checked constraints</summary>

**Constraints checked:** All available constraints

</details>

## Tool Scorecards (🤖)

<details>
<summary>Toggle details</summary>

### echo

**Score:** 9/10 (90%)

[→ View tool details](#tool-echo)

<details>
<summary>Toggle scorecard details</summary>

<details>
<summary>Tool Name (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The name 'echo' is concise and adheres to a short length, making it easy to remember and use. |
| Uniqueness | ✅ | The name 'echo' is commonly used in programming contexts but is unique enough within the scope of this tool's functionality. |
| Descriptiveness | ✅ | The name 'echo' accurately describes the tool's purpose of echoing back the input. |

</details>

<details>
<summary>Tool Description (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The description is concise and provides sufficient information about the tool's functionality. |
| Parameters | ✅ | The description mentions the tool echoes back the input, which aligns with the 'message' parameter in the schema. |
| Examples | ❌ | The description does not provide any examples of usage, which would improve clarity and usability. |

</details>

<details>
<summary>Input Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ✅ | The input schema is simple and easy to understand, with only one required parameter. |
| Parameters | ✅ | The schema defines a single parameter, 'message', which is clearly described and aligns with the tool's purpose. |
| Optionals | ✅ | The schema does not include any optional parameters, which is appropriate for a tool with such a straightforward function. |
| Constraints | ✅ | The schema enforces constraints such as requiring the 'message' parameter and disallowing additional properties, ensuring proper input validation. |

</details>

<details>
<summary>Output Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ⚪ | The output schema is not explicitly defined in the provided information, so it cannot be evaluated. |
| Parameters | ⚪ | The output schema is not explicitly defined in the provided information, so it cannot be evaluated. |
| Optionals | ⚪ | The output schema is not explicitly defined in the provided information, so it cannot be evaluated. |
| Constraints | ⚪ | The output schema is not explicitly defined in the provided information, so it cannot be evaluated. |

</details>

</details>

### add

**Score:** 8/10 (80%)

[→ View tool details](#tool-add)

<details>
<summary>Toggle scorecard details</summary>

<details>
<summary>Tool Name (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The name 'add' is concise and appropriately short for its purpose. |
| Uniqueness | ❌ | The name 'add' is very generic and likely to conflict with other tools or functions in a broader context. |
| Descriptiveness | ✅ | The name 'add' clearly describes the tool's functionality of adding two numbers. |

</details>

<details>
<summary>Tool Description (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The description is concise and to the point, providing a clear understanding of the tool's purpose. |
| Parameters | ✅ | The description mentions that the tool adds two numbers, which aligns with the parameters 'a' and 'b' in the schema. |
| Examples | ❌ | The description does not provide any examples of how the tool can be used. |

</details>

<details>
<summary>Input Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ✅ | The input schema is simple and easy to understand, with only two required parameters. |
| Parameters | ✅ | The schema defines two parameters, 'a' and 'b', which are clearly described and required. |
| Optionals | ✅ | The schema does not include any optional parameters, which is appropriate for a simple addition tool. |
| Constraints | ✅ | The schema enforces constraints such as requiring both 'a' and 'b' and disallowing additional properties, ensuring input validity. |

</details>

<details>
<summary>Output Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ⚪ | The output schema is not provided, so it cannot be evaluated. |
| Parameters | ⚪ | The output schema is not provided, so it cannot be evaluated. |
| Optionals | ⚪ | The output schema is not provided, so it cannot be evaluated. |
| Constraints | ⚪ | The output schema is not provided, so it cannot be evaluated. |

</details>

</details>

### longRunningOperation

**Score:** 8/10 (80%)

[→ View tool details](#tool-longRunningOperation)

<details>
<summary>Toggle scorecard details</summary>

<details>
<summary>Tool Name (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The name 'longRunningOperation' is concise and does not exceed a reasonable length. |
| Uniqueness | ✅ | The name appears unique and unlikely to conflict with other tools, as it describes a specific functionality. |
| Descriptiveness | ✅ | The name clearly conveys the purpose of the tool, which is to handle long-running operations. |

</details>

<details>
<summary>Tool Description (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The description is concise and provides enough information without being overly verbose. |
| Parameters | ✅ | The description mentions progress updates and aligns with the parameters in the schema (duration and steps). |
| Examples | ❌ | The description does not provide any examples or use cases to illustrate how the tool might be used. |

</details>

<details>
<summary>Input Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ✅ | The schema is simple and easy to understand, with only two parameters (duration and steps). |
| Parameters | ✅ | The schema defines clear parameters with descriptions, types, and default values. |
| Optionals | ✅ | Both parameters have default values, making them optional for the user to specify. |
| Constraints | ❌ | The schema does not define constraints (e.g., minimum or maximum values) for the parameters, which could lead to invalid or nonsensical inputs. |

</details>

<details>
<summary>Output Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ⚪ | The output schema is not provided, so its complexity cannot be evaluated. |
| Parameters | ⚪ | The output schema is not provided, so the parameters cannot be evaluated. |
| Optionals | ⚪ | The output schema is not provided, so optional fields cannot be evaluated. |
| Constraints | ⚪ | The output schema is not provided, so constraints cannot be evaluated. |

</details>

</details>

### printEnv

**Score:** 7/8 (88%)

[→ View tool details](#tool-printEnv)

<details>
<summary>Toggle scorecard details</summary>

<details>
<summary>Tool Name (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The name 'printEnv' is concise and adheres to a reasonable length for a tool name. |
| Uniqueness | ✅ | The name 'printEnv' is unique enough to convey its purpose without ambiguity. |
| Descriptiveness | ✅ | The name clearly describes the tool's functionality, which is to print environment variables. |

</details>

<details>
<summary>Tool Description (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The description is concise and provides sufficient information about the tool's purpose. |
| Parameters | ⚪ | The description does not mention parameters, which is acceptable as the tool does not require any input parameters. |
| Examples | ❌ | The description does not provide any examples of usage, which would be helpful for understanding the tool's application. |

</details>

<details>
<summary>Input Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ✅ | The input schema is simple and appropriate for a tool that does not require any input parameters. |
| Parameters | ✅ | The schema correctly defines no input parameters, aligning with the tool's functionality. |
| Optionals | ⚪ | There are no optional parameters, which is consistent with the tool's design. |
| Constraints | ✅ | The schema enforces no additional properties, ensuring that the tool does not accept unexpected inputs. |

</details>

<details>
<summary>Output Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ⚪ | The output schema is not provided, so it cannot be evaluated. |
| Parameters | ⚪ | The output schema is not provided, so it cannot be evaluated. |
| Optionals | ⚪ | The output schema is not provided, so it cannot be evaluated. |
| Constraints | ⚪ | The output schema is not provided, so it cannot be evaluated. |

</details>

</details>

### sampleLLM

**Score:** 7/10 (70%)

[→ View tool details](#tool-sampleLLM)

<details>
<summary>Toggle scorecard details</summary>

<details>
<summary>Tool Name (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The name 'sampleLLM' is concise and adheres to a reasonable length for a tool name. |
| Uniqueness | ❌ | The name 'sampleLLM' is generic and does not stand out as unique, as it could apply to many tools related to LLM sampling. |
| Descriptiveness | ✅ | The name 'sampleLLM' is descriptive enough to convey the tool's purpose of sampling from an LLM. |

</details>

<details>
<summary>Tool Description (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The description is concise and provides a clear understanding of the tool's functionality without being overly verbose. |
| Parameters | ✅ | The description mentions the use of MCP's sampling feature, which aligns with the tool's functionality and parameters. |
| Examples | ❌ | The description does not provide any examples of how the tool can be used, which would improve clarity and usability. |

</details>

<details>
<summary>Input Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ✅ | The input schema is simple and easy to understand, with only two parameters: 'prompt' and 'maxTokens'. |
| Parameters | ✅ | The schema clearly defines the required and optional parameters, including their types and descriptions. |
| Optionals | ✅ | The schema includes a default value for the optional 'maxTokens' parameter, which is a good practice. |
| Constraints | ❌ | The schema does not specify constraints for the 'maxTokens' parameter, such as a minimum or maximum value, which could lead to misuse. |

</details>

<details>
<summary>Output Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ⚪ | The output schema is not provided, so its complexity cannot be evaluated. |
| Parameters | ⚪ | The output schema is not provided, so the parameters cannot be evaluated. |
| Optionals | ⚪ | The output schema is not provided, so optional parameters cannot be evaluated. |
| Constraints | ⚪ | The output schema is not provided, so constraints cannot be evaluated. |

</details>

</details>

### getTinyImage

**Score:** 5/9 (56%)

[→ View tool details](#tool-getTinyImage)

<details>
<summary>Toggle scorecard details</summary>

<details>
<summary>Tool Name (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The name 'getTinyImage' is concise and appropriately short. |
| Uniqueness | ✅ | The name 'getTinyImage' appears unique and unlikely to conflict with other tool names. |
| Descriptiveness | ❌ | The name 'getTinyImage' does not provide enough context about what 'MCP_TINY_IMAGE' is or its purpose. |

</details>

<details>
<summary>Tool Description (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The description is short and to the point, which is appropriate for a tool description. |
| Parameters | ❌ | The description does not explain the parameters or inputs required by the tool. |
| Examples | ❌ | The description does not provide any examples of usage or outputs. |

</details>

<details>
<summary>Input Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ✅ | The input schema is simple and does not introduce unnecessary complexity. |
| Parameters | ❌ | The input schema does not define any parameters, which limits the tool's functionality and flexibility. |
| Optionals | ⚪ | There are no optional parameters to evaluate since the schema does not define any parameters. |
| Constraints | ✅ | The schema explicitly disallows additional properties, which enforces strict input validation. |

</details>

<details>
<summary>Output Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ⚪ | The output schema is not provided, so complexity cannot be evaluated. |
| Parameters | ⚪ | The output schema is not provided, so parameters cannot be evaluated. |
| Optionals | ⚪ | The output schema is not provided, so optional parameters cannot be evaluated. |
| Constraints | ⚪ | The output schema is not provided, so constraints cannot be evaluated. |

</details>

</details>

### annotatedMessage

**Score:** 9/10 (90%)

[→ View tool details](#tool-annotatedMessage)

<details>
<summary>Toggle scorecard details</summary>

<details>
<summary>Tool Name (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The name 'annotatedMessage' is concise and adheres to a reasonable length for a tool name. |
| Uniqueness | ✅ | The name appears unique and does not conflict with common tool names, making it easily distinguishable. |
| Descriptiveness | ✅ | The name effectively conveys the purpose of the tool, which is related to annotations and messages. |

</details>

<details>
<summary>Tool Description (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The description is concise and provides sufficient information without being overly verbose. |
| Parameters | ✅ | The description mentions the use of annotations and metadata, which aligns with the parameters in the schema. |
| Examples | ❌ | The description does not provide any examples or use cases to illustrate the tool's functionality. |

</details>

<details>
<summary>Input Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ✅ | The schema is straightforward, with only two properties and clear constraints, making it easy to understand. |
| Parameters | ✅ | The schema defines parameters ('messageType' and 'includeImage') that are relevant and well-documented. |
| Optionals | ✅ | The 'includeImage' parameter is optional with a default value, providing flexibility without overcomplicating the schema. |
| Constraints | ✅ | The schema includes constraints such as 'enum' for 'messageType' and 'required' fields, ensuring valid input. |

</details>

<details>
<summary>Output Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ⚪ | The output schema is not provided, so its complexity cannot be evaluated. |
| Parameters | ⚪ | The output schema is not provided, so the parameters cannot be evaluated. |
| Optionals | ⚪ | The output schema is not provided, so optional fields cannot be evaluated. |
| Constraints | ⚪ | The output schema is not provided, so constraints cannot be evaluated. |

</details>

</details>

### getResourceReference

**Score:** 9/10 (90%)

[→ View tool details](#tool-getResourceReference)

<details>
<summary>Toggle scorecard details</summary>

<details>
<summary>Tool Name (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The name 'getResourceReference' is concise and within a reasonable length for a tool name. |
| Uniqueness | ✅ | The name appears unique and specific to the functionality of returning a resource reference. |
| Descriptiveness | ✅ | The name clearly describes the purpose of the tool, which is to get a resource reference. |

</details>

<details>
<summary>Tool Description (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The description is concise and provides enough information about the tool's purpose. |
| Parameters | ✅ | The description mentions that the tool returns a resource reference and is intended for MCP clients, aligning with the input schema. |
| Examples | ❌ | The description does not provide any examples of how the tool might be used or what the output looks like. |

</details>

<details>
<summary>Input Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ✅ | The input schema is simple and easy to understand, with only one required parameter. |
| Parameters | ✅ | The schema defines a single parameter, 'resourceId', with clear constraints and a description. |
| Optionals | ✅ | The schema does not include any optional parameters, which is appropriate for this tool. |
| Constraints | ✅ | The schema includes clear constraints for 'resourceId' (minimum: 1, maximum: 100), ensuring valid input. |

</details>

<details>
<summary>Output Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ⚪ | The output schema is not provided, so complexity cannot be evaluated. |
| Parameters | ⚪ | The output schema is not provided, so parameters cannot be evaluated. |
| Optionals | ⚪ | The output schema is not provided, so optional parameters cannot be evaluated. |
| Constraints | ⚪ | The output schema is not provided, so constraints cannot be evaluated. |

</details>

</details>

### startElicitation

**Score:** 5/9 (56%)

[→ View tool details](#tool-startElicitation)

<details>
<summary>Toggle scorecard details</summary>

<details>
<summary>Tool Name (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The name 'startElicitation' is concise and does not exceed a reasonable length. |
| Uniqueness | ✅ | The name 'startElicitation' appears unique and is unlikely to conflict with other tools. |
| Descriptiveness | ✅ | The name 'startElicitation' is descriptive and gives a clear indication of the tool's purpose, which is to initiate an elicitation process. |

</details>

<details>
<summary>Tool Description (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The description is concise and provides sufficient information about the tool's functionality without being overly verbose. |
| Parameters | ❌ | The description does not explicitly mention the parameters or inputs required by the tool, which could lead to ambiguity. |
| Examples | ❌ | The description does not provide any examples of how the tool might be used, which would help clarify its functionality. |

</details>

<details>
<summary>Input Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ✅ | The input schema is simple and does not introduce unnecessary complexity. |
| Parameters | ❌ | The input schema does not define any parameters, which contradicts the tool's purpose of eliciting information about the user's favorite color, number, and pets. |
| Optionals | ⚪ | The schema does not define any parameters, so the concept of optional fields is not applicable. |
| Constraints | ❌ | The schema does not define any constraints, which could lead to a lack of validation for the expected inputs. |

</details>

<details>
<summary>Output Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ⚪ | The output schema is not provided, so its complexity cannot be evaluated. |
| Parameters | ⚪ | The output schema is not provided, so the presence or absence of parameters cannot be evaluated. |
| Optionals | ⚪ | The output schema is not provided, so the concept of optional fields is not applicable. |
| Constraints | ⚪ | The output schema is not provided, so the presence of constraints cannot be evaluated. |

</details>

</details>

### getResourceLinks

**Score:** 9/10 (90%)

[→ View tool details](#tool-getResourceLinks)

<details>
<summary>Toggle scorecard details</summary>

<details>
<summary>Tool Name (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The name 'getResourceLinks' is concise and within a reasonable length for a tool name. |
| Uniqueness | ✅ | The name appears unique and does not conflict with common tool names, making it easily identifiable. |
| Descriptiveness | ✅ | The name clearly conveys the purpose of the tool, which is to retrieve resource links. |

</details>

<details>
<summary>Tool Description (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The description is concise and provides sufficient information about the tool's functionality. |
| Parameters | ✅ | The description mentions that the tool returns multiple resource links and references different types of resources, aligning with the input schema. |
| Examples | ❌ | The description does not provide any examples of the types of resource links or use cases, which would improve clarity. |

</details>

<details>
<summary>Input Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ✅ | The input schema is simple and easy to understand, with only one parameter ('count') and clear constraints. |
| Parameters | ✅ | The schema defines the 'count' parameter with clear properties, including type, range, and default value. |
| Optionals | ✅ | The schema includes a default value for the 'count' parameter, making it optional for users to specify. |
| Constraints | ✅ | The schema enforces constraints on the 'count' parameter, such as a minimum of 1 and a maximum of 10, ensuring valid input. |

</details>

<details>
<summary>Output Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ⚪ | The output schema is not provided, so its complexity cannot be evaluated. |
| Parameters | ⚪ | The output schema is not provided, so the parameters cannot be evaluated. |
| Optionals | ⚪ | The output schema is not provided, so optional properties cannot be evaluated. |
| Constraints | ⚪ | The output schema is not provided, so constraints cannot be evaluated. |

</details>

</details>

### structuredContent

**Score:** 13/14 (93%)

[→ View tool details](#tool-structuredContent)

<details>
<summary>Toggle scorecard details</summary>

<details>
<summary>Tool Name (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The name 'structuredContent' is concise and adheres to a reasonable length for a tool name. |
| Uniqueness | ✅ | The name 'structuredContent' is unique enough to distinguish it from generic tool names, though it could be more specific. |
| Descriptiveness | ✅ | The name 'structuredContent' provides a clear indication of the tool's purpose, which is to handle structured data. |

</details>

<details>
<summary>Tool Description (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Length | ✅ | The description is concise and provides sufficient information about the tool's functionality without being overly verbose. |
| Parameters | ✅ | The description mentions that the tool returns structured content and includes an output schema for client data validation, which aligns with the provided schemas. |
| Examples | ❌ | The description does not include any examples to illustrate the tool's usage or output, which would improve clarity. |

</details>

<details>
<summary>Input Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ✅ | The input schema is simple and easy to understand, requiring only a 'location' field with clear constraints. |
| Parameters | ✅ | The input schema defines a single required parameter ('location') with a clear description and constraints. |
| Optionals | ✅ | The schema does not include optional parameters, which is appropriate given the simplicity of the tool's functionality. |
| Constraints | ✅ | The schema includes appropriate constraints, such as 'minLength: 1' for the 'location' field, ensuring valid input. |

</details>

<details>
<summary>Output Schema (🤖)</summary>

| Aspect | Score | Justification |
| --- | --- | --- |
| Complexity | ✅ | The output schema is straightforward, with three well-defined properties: 'temperature', 'conditions', and 'humidity'. |
| Parameters | ✅ | The output schema includes all necessary parameters to describe weather data, each with clear descriptions. |
| Optionals | ✅ | The schema does not include optional properties, which is appropriate for the tool's purpose of providing complete weather data. |
| Constraints | ✅ | The schema enforces constraints such as requiring all properties and disallowing additional properties, ensuring data consistency. |

</details>

</details>

</details>

## Functional Test Results

<details>
<summary>Toggle details</summary>

**Test Plan (🤖):**
```
This testing plan systematically evaluates the functionality, dependencies, and quality of the MCP server tools. The plan starts with foundational tools, progresses to more complex ones, and includes realistic arguments, edge cases, and expected outputs. Dependencies are respected, and tools are tested in a logical sequence to ensure comprehensive coverage.
```

**Overall Evaluation (🤖):**
- ✅ **Meets Expectations**: The majority of tools executed successfully without errors. Most tools returned the expected outputs, and the server demonstrated robust functionality across foundational, arithmetic, long-running, and complex tools. Only a few tools encountered errors, which were handled gracefully.
- **Error Type**: N/A - No critical authentication or connection errors were observed during the evaluation. Errors encountered were limited to specific tools and were related to invalid inputs or edge cases, which were appropriately managed by the server.

### Test Steps

#### Step 1: echo

<details>
<summary>Toggle step details</summary>

Score (🤖): 5/6

[→ View tool details](#tool-echo)

**Purpose (🤖):** The echo tool is foundational and has no dependencies. Testing it first ensures basic functionality of the server.

**Tool Call (🤖):**
```json
{
  "message": "Hello, MCP!"
}
```
**Expected (🤖):** The tool should return the input message: 'Hello, MCP!'

**Actual Output (1 blocks):**

```
Echo: Hello, MCP!
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 6 |
| Text blocks | 1 |

**Evaluation (🤖):**
- ❌ **Meets Expectations**: The actual output does not exactly match the expected output. The expected output was 'Hello, MCP!', but the actual output prepended 'Echo: ' to the message.
- ✅ **Output Quality**: The output is clear, well-structured, and includes the expected echoed message.
- ✅ **Output Relevance**: The output is relevant to the input parameters, as it echoes the provided message.
- ✅ **Schema Compliance**: The output adheres to the expected schema, with content properly structured in the TextContent format.
- ⚪ **Error Type**: No errors occurred, so error type evaluation is not applicable.
- ✅ **No Silent Error**: The tool call explicitly returned a response without any silent failures.
- ✅ **Error Handling**: The tool call did not produce any errors, and the isError flag is set to False.
</details>

#### Step 2: add

<details>
<summary>Toggle step details</summary>

Score (🤖): 5/6

[→ View tool details](#tool-add)

**Purpose (🤖):** The add tool is simple and independent. Testing it ensures basic arithmetic functionality.

**Tool Call (🤖):**
```json
{
  "a": 5,
  "b": 10
}
```
**Expected (🤖):** The tool should return the sum: 15

**Actual Output (1 blocks):**

```
The sum of 5 and 10 is 15.
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 12 |
| Text blocks | 1 |

**Evaluation (🤖):**
- ✅ **Meets Expectations**: Despite the schema compliance issue, the tool call meets the functional expectations by providing the correct sum in a comprehensible format.
- ✅ **Output Quality**: The output is clear, accurate, and provides the correct sum of the input parameters (5 + 10 = 15).
- ✅ **Output Relevance**: The output is relevant to the input parameters and matches the expected operation of summing the two numbers.
- ❌ **Schema Compliance**: The output does not strictly adhere to the expected schema. The result is embedded in a text field instead of being returned as a structured numerical value.
- ⚪ **Error Type**: No errors occurred during the tool call, so error type evaluation is not applicable.
- ✅ **No Silent Error**: The tool call explicitly returned a result without any indication of silent failure.
- ✅ **Error Handling**: The tool call did not produce any errors, and the isError flag is set to False.
</details>

#### Step 3: add

<details>
<summary>Toggle step details</summary>

Score (🤖): 6/6

[→ View tool details](#tool-add)

**Purpose (🤖):** Testing with a mix of positive and negative numbers ensures the tool handles all number types correctly.

**Tool Call (🤖):**
```json
{
  "a": -3,
  "b": 7
}
```
**Expected (🤖):** The tool should return the sum: 4

**Actual Output (1 blocks):**

```
The sum of -3 and 7 is 4.
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 12 |
| Text blocks | 1 |

**Evaluation (🤖):**
- ✅ **Meets Expectations**: The tool call meets all expectations by providing the correct result, adhering to the schema, and handling the operation without errors.
- ✅ **Output Quality**: The output correctly states the sum of -3 and 7 as 4, which matches the expected result.
- ✅ **Output Relevance**: The output is directly relevant to the input parameters and the expected operation (addition).
- ✅ **Schema Compliance**: The output adheres to the expected schema, with content provided in the correct format and no structural issues.
- ⚪ **Error Type**: No errors occurred, so error type evaluation is not applicable.
- ✅ **No Silent Error**: The tool call explicitly returned a valid response without any silent failures.
- ✅ **Error Handling**: The tool call did not produce any errors, and the isError flag is correctly set to False.
</details>

#### Step 4: longRunningOperation

<details>
<summary>Toggle step details</summary>

Score (🤖): 4/6

[→ View tool details](#tool-longRunningOperation)

**Purpose (🤖):** This tool demonstrates long-running operations. Testing ensures progress updates and completion behavior.

**Tool Call (🤖):**
```json
{
  "duration": 5,
  "steps": 3
}
```
**Expected (🤖):** The tool should return progress updates and complete after 5 seconds.

**Actual Output (1 blocks):**

```
Long running operation completed. Duration: 5 seconds, Steps: 3.
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 16 |
| Text blocks | 1 |

**Evaluation (🤖):**
- ❌ **Meets Expectations**: The tool did not fully meet expectations as it failed to provide progress updates during the operation.
- ✅ **Output Quality**: The final output was clear, accurate, and aligned with the input parameters (duration: 5 seconds, steps: 3).
- ❌ **Output Relevance**: The tool did not provide progress updates during the operation, which was part of the expected output.
- ✅ **Schema Compliance**: The output adhered to the expected schema, with content provided in the correct format.
- ⚪ **Error Type**: No errors occurred during the tool call, so error type evaluation is not applicable.
- ✅ **No Silent Error**: There were no silent errors; the tool provided a clear and complete response.
- ✅ **Error Handling**: The tool call completed without any errors, as indicated by isError=False.
</details>

#### Step 5: printEnv

<details>
<summary>Toggle step details</summary>

Score (🤖): 6/6

[→ View tool details](#tool-printEnv)

**Purpose (🤖):** This tool is used to debug the server's environment. Testing ensures it correctly retrieves and displays environment variables.

**Tool Call (🤖):**
```json
{}
```
**Expected (🤖):** The tool should return a list of environment variables.

**Actual Output (1 blocks):**

```json
{
  "NODE": "/Users/tylerpayne/.nvm/versions/node/v22.16.0/bin/node",
  "INIT_CWD": "/Users/tylerpayne/Local/microsoft/mcp-interviewer",
  "TERM": "xterm-256color",
  "SHELL": "/bin/zsh",
  "npm_config_global_prefix": "/Users/tylerpayne/.nvm/versions/node/v22.16.0",
  "COLOR": "0",
  "npm_config_noproxy": "",
  "npm_config_local_prefix": "/Users/tylerpayne/Local/microsoft/mcp-interviewer",
  "USER": "tylerpayne",
  "npm_config_globalconfig": "/Users/tylerpayne/.nvm/versions/node/v22.16.0/etc/npm
... (2654 chars truncated)
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 1,026 |
| Text blocks | 1 |

**Evaluation (🤖):**
- ✅ **Meets Expectations**: The tool call met all expectations by returning the environment variables as required without any issues.
- ✅ **Output Quality**: The output is well-structured, complete, and provides the environment variables in a readable JSON format.
- ✅ **Output Relevance**: The output contains a list of environment variables, which aligns with the expected functionality of the tool.
- ✅ **Schema Compliance**: The output adheres to the expected schema, providing the environment variables in a structured JSON format.
- ⚪ **Error Type**: No errors occurred during the tool call, so error type classification is not applicable.
- ✅ **No Silent Error**: The tool call executed without any silent failures, and the output was provided as expected.
- ✅ **Error Handling**: The tool call did not encounter any errors, and the output was successfully returned.
</details>

#### Step 6: sampleLLM

<details>
<summary>Toggle step details</summary>

Score (🤖): 3/6

[→ View tool details](#tool-sampleLLM)

**Purpose (🤖):** Testing the LLM sampling tool ensures it generates responses based on the given prompt.

**Tool Call (🤖):**
```json
{
  "prompt": "What is the capital of France?",
  "maxTokens": 10
}
```
**Expected (🤖):** The tool should return a response like 'The capital of France is Paris.'

**Actual Output (1 blocks):**

```
LLM sampling result: Dummy content
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 7 |
| Text blocks | 1 |

**MCP Requests:**

| Request Type | Count |
| --- | --- |
| Sampling | 1 |

**Evaluation (🤖):**
- ❌ **Meets Expectations**: The tool's output does not meet the expectations, as it fails to provide the correct or relevant answer to the input prompt.
- ❌ **Output Quality**: The output does not provide a meaningful or accurate response to the input prompt. It is generic and unrelated to the expected answer.
- ❌ **Output Relevance**: The actual output ('LLM sampling result: Dummy content') is not relevant to the input prompt ('What is the capital of France?').
- ✅ **Schema Compliance**: The output adheres to the expected schema, with content provided in the correct structure.
- ⚪ **Error Type**: No errors occurred, so no specific error type is applicable.
- ✅ **No Silent Error**: The tool explicitly indicated no errors occurred, and there is no evidence of silent failure.
- ✅ **Error Handling**: The tool call did not produce any errors, as indicated by isError=False.
</details>

#### Step 7: getTinyImage

<details>
<summary>Toggle step details</summary>

Score (🤖): 6/6

[→ View tool details](#tool-getTinyImage)

**Purpose (🤖):** This tool retrieves a predefined image. Testing ensures the image is returned correctly.

**Tool Call (🤖):**
```json
{}
```
**Expected (🤖):** The tool should return the MCP_TINY_IMAGE.

**Actual Output (3 blocks):**

```
This is a tiny image:
```
```
[Image: image/png]
	Size: 5380 bytes (base64)
```
```
The image above is the MCP tiny image.
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 14 |
| Text blocks | 2 |
| Image blocks | 1 |

**Evaluation (🤖):**
- ✅ **Meets Expectations**: The tool call successfully returned the expected MCP_TINY_IMAGE along with appropriate descriptive text, fulfilling the requirements.
- ✅ **Output Quality**: The output contains a valid image encoded in base64 format and descriptive text, meeting quality expectations.
- ✅ **Output Relevance**: The output includes the expected MCP_TINY_IMAGE along with relevant text content describing the image.
- ✅ **Schema Compliance**: The output adheres to the expected schema, including meta, content, and structuredContent fields.
- ⚪ **Error Type**: No errors occurred during the tool call, so error type evaluation is not applicable.
- ✅ **No Silent Error**: The tool call explicitly returned output without any indication of silent failure.
- ✅ **Error Handling**: The tool call did not produce any errors, and the isError flag is set to false.
</details>

#### Step 8: annotatedMessage

<details>
<summary>Toggle step details</summary>

Score (🤖): 6/6

[→ View tool details](#tool-annotatedMessage)

**Purpose (🤖):** Testing this tool ensures it correctly generates annotated messages with optional images.

**Tool Call (🤖):**
```json
{
  "messageType": "success",
  "includeImage": true
}
```
**Expected (🤖):** The tool should return a success message with an example image.

**Actual Output (2 blocks):**

```
Operation completed successfully
```
```
[Image: image/png]
	Size: 5380 bytes (base64)
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 3 |
| Text blocks | 1 |
| Image blocks | 1 |

**Evaluation (🤖):**
- ✅ **Meets Expectations**: The tool call meets all expectations by providing the correct success message and an example image as specified in the input parameters.
- ✅ **Output Quality**: The success message is clear and the image is provided in a valid format (PNG). Both components meet quality expectations.
- ✅ **Output Relevance**: The output includes a success message and an image, which aligns with the expected output based on the input parameters.
- ✅ **Schema Compliance**: The output adheres to the expected schema, with properly structured text and image content, including annotations and metadata.
- ⚪ **Error Type**: No errors occurred during the tool call, so error type evaluation is not applicable.
- ✅ **No Silent Error**: The tool call explicitly returned content and did not fail silently.
- ✅ **Error Handling**: The tool call did not produce any errors, and the isError flag is set to false.
</details>

#### Step 9: getResourceReference

<details>
<summary>Toggle step details</summary>

Score (🤖): 6/6

[→ View tool details](#tool-getResourceReference)

**Purpose (🤖):** This tool retrieves a resource reference. Testing ensures it handles valid resource IDs correctly.

**Tool Call (🤖):**
```json
{
  "resourceId": 42
}
```
**Expected (🤖):** The tool should return a reference for resource ID 42.

**Actual Output (3 blocks):**

```
Returning resource reference for Resource 42:
```
```
[Embedded Resource: test://static/resource/42]
	MIME type: application/octet-stream
	Blob size: 48 bytes (base64)
```
```
You can access this resource using the URI: test://static/resource/42
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 23 |
| Text blocks | 2 |
| Resource | 1 |

**Evaluation (🤖):**
- ✅ **Meets Expectations**: The tool call meets the expectations by successfully returning a reference for resource ID 42, as specified in the task.
- ✅ **Output Quality**: The output includes detailed and well-structured information, such as a URI, MIME type, and base64-encoded blob, which are appropriate for the requested resource reference.
- ✅ **Output Relevance**: The output is relevant to the input parameters, as it provides a reference for resource ID 42, including a URI and additional context.
- ✅ **Schema Compliance**: The output adheres to the expected schema, including the use of 'meta', 'content', and 'structuredContent' fields, and the data types are consistent with the schema.
- ⚪ **Error Type**: No errors occurred during the tool call, so error type classification is not applicable.
- ✅ **No Silent Error**: The tool call explicitly returned content and did not fail silently.
- ✅ **Error Handling**: The tool call did not produce any errors, and the 'isError' flag is set to False.
</details>

#### Step 10: getResourceReference

<details>
<summary>Toggle step details</summary>

Score (🤖): 0/6

[→ View tool details](#tool-getResourceReference)

**Purpose (🤖):** Testing with an out-of-range resource ID ensures the tool handles invalid inputs gracefully.

**Tool Call (🤖):**
```json
{
  "resourceId": 101
}
```
**Expected (🤖):** The tool should return an error indicating the resource ID is out of range.

**Exception:**
```
[
  {
    "code": "too_big",
    "maximum": 100,
    "type": "number",
    "inclusive": true,
    "exact": false,
    "message": "Number must be less than or equal to 100",
    "path": [
      "resourceId"
    ]
  }
]
```

**Evaluation (🤖):**
- ❌ **Meets Expectations**: The tool did not meet expectations as it failed to handle the out-of-range resource ID appropriately.
- ❌ **Output Quality**: No output was provided, so the quality of the output cannot be assessed.
- ❌ **Output Relevance**: The output was irrelevant as it did not address the expected error condition.
- ❌ **Schema Compliance**: The tool did not return any output, which violates the expected schema for error handling.
- ⚪ **Error Type**: No error was returned, so the error type could not be determined.
- ❌ **No Silent Error**: The tool failed silently by returning no output instead of an error message.
- ❌ **Error Handling**: The tool did not return the expected error message for an out-of-range resource ID.
</details>

#### Step 11: startElicitation

<details>
<summary>Toggle step details</summary>

Score (🤖): 3/6

[→ View tool details](#tool-startElicitation)

**Purpose (🤖):** This tool demonstrates elicitation. Testing ensures it correctly prompts the user for input.

**Tool Call (🤖):**
```json
{}
```
**Expected (🤖):** The tool should prompt the user for their favorite color, number, and pets.

**Actual Output (2 blocks):**

```
⚠️ User cancelled the elicitation dialog.
```
```

Raw result: {
  "action": "cancel"
}
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 22 |
| Text blocks | 2 |

**MCP Requests:**

| Request Type | Count |
| --- | --- |
| Elicitation | 1 |

**Evaluation (🤖):**
- ❌ **Meets Expectations**: The tool did not meet the expectations of prompting the user for their favorite color, number, and pets due to the cancellation.
- ❌ **Output Quality**: The output did not fulfill the expected elicitation task, and the content provided was not aligned with the intended functionality.
- ❌ **Output Relevance**: The output did not meet the expected behavior of prompting the user for their favorite color, number, and pets. Instead, it reported a cancellation.
- ✅ **Schema Compliance**: The output adhered to the expected schema structure, including meta and content fields.
- ⚪ **Error Type**: No specific error occurred; the user explicitly cancelled the elicitation dialog.
- ✅ **No Silent Error**: The tool provided explicit feedback about the cancellation, ensuring no silent failure occurred.
- ✅ **Error Handling**: The tool handled the user cancellation gracefully by providing a clear message indicating the dialog was cancelled.
</details>

#### Step 12: getResourceLinks

<details>
<summary>Toggle step details</summary>

Score (🤖): 6/6

[→ View tool details](#tool-getResourceLinks)

**Purpose (🤖):** This tool retrieves multiple resource links. Testing ensures it handles valid counts correctly.

**Tool Call (🤖):**
```json
{
  "count": 5
}
```
**Expected (🤖):** The tool should return 5 resource links.

**Actual Output (6 blocks):**

```
Here are 5 resource links to resources available in this server (see full output in tool response if your client does not support resource_link yet):
```
```
Resource Link: test://static/resource/1
	MIME type: text/plain
	Description: Resource 1: plaintext resource
```
```
Resource Link: test://static/resource/2
	MIME type: application/octet-stream
	Description: Resource 2: binary blob resource
```
```
Resource Link: test://static/resource/3
	MIME type: text/plain
	Description: Resource 3: plaintext resource
```
```
Resource Link: test://static/resource/4
	MIME type: application/octet-stream
	Description: Resource 4: binary blob resource
```
```
Resource Link: test://static/resource/5
	MIME type: text/plain
	Description: Resource 5: plaintext resource
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 29 |
| Text blocks | 1 |
| Resource link blocks | 5 |

**Evaluation (🤖):**
- ✅ **Meets Expectations**: The tool call met the expectations by returning exactly 5 resource links as specified in the input parameters.
- ✅ **Output Quality**: The output includes a clear description, valid URIs, and appropriate metadata for each resource link. The content is well-structured and informative.
- ✅ **Output Relevance**: The output is relevant to the input parameters, providing 5 resource links as requested.
- ✅ **Schema Compliance**: The output adheres to the expected schema, including the correct structure for TextContent and ResourceLink objects.
- ⚪ **Error Type**: No errors occurred during the tool call, so error type classification is not applicable.
- ✅ **No Silent Error**: The tool call explicitly indicated no errors, and the output aligns with the expected behavior.
- ✅ **Error Handling**: The tool call did not encounter any errors, and the isError flag is set to False.
</details>

#### Step 13: getResourceLinks

<details>
<summary>Toggle step details</summary>

Score (🤖): 0/6

[→ View tool details](#tool-getResourceLinks)

**Purpose (🤖):** Testing with an out-of-range count ensures the tool handles invalid inputs gracefully.

**Tool Call (🤖):**
```json
{
  "count": 0
}
```
**Expected (🤖):** The tool should return an error indicating the count is out of range.

**Exception:**
```
[
  {
    "code": "too_small",
    "minimum": 1,
    "type": "number",
    "inclusive": true,
    "exact": false,
    "message": "Number must be greater than or equal to 1",
    "path": [
      "count"
    ]
  }
]
```

**Evaluation (🤖):**
- ❌ **Meets Expectations**: The tool did not meet expectations because it failed to handle the invalid input appropriately and did not return the expected error.
- ❌ **Output Quality**: The output quality is poor because it did not meet the expected behavior of returning an error for an invalid input.
- ❌ **Output Relevance**: The output was not relevant to the input parameters, as it did not provide the expected error message.
- ❌ **Schema Compliance**: The output did not comply with the expected schema, as it returned 'None' instead of an error object.
- Bad Request **Error Type**: The expected error type for an out-of-range parameter is a 'Bad Request', but no error was returned.
- ❌ **No Silent Error**: The tool silently failed by returning 'None' instead of an appropriate error message.
- ❌ **Error Handling**: The tool did not return an error as expected when the count parameter was out of range.
</details>

#### Step 14: structuredContent

<details>
<summary>Toggle step details</summary>

Score (🤖): 6/6

[→ View tool details](#tool-structuredContent)

**Purpose (🤖):** This tool returns structured content. Testing ensures it retrieves weather data for a valid location.

**Tool Call (🤖):**
```json
{
  "location": "New York"
}
```
**Expected (🤖):** The tool should return structured weather data for New York, including temperature, conditions, and humidity.

**Actual Output (1 blocks):**

```json
{
  "temperature": 22.5,
  "conditions": "Partly cloudy",
  "humidity": 65
}
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 17 |
| Text blocks | 1 |

**Evaluation (🤖):**
- ✅ **Meets Expectations**: The tool call met all expectations by providing accurate, relevant, and well-structured weather data for New York.
- ✅ **Output Quality**: The output includes all expected fields (temperature, conditions, humidity) with appropriate values.
- ✅ **Output Relevance**: The output is directly relevant to the input parameters, providing weather data for New York as requested.
- ✅ **Schema Compliance**: The structuredContent output adheres to the expected schema for weather data.
- ⚪ **Error Type**: No errors occurred, so error type classification is not applicable.
- ✅ **No Silent Error**: The tool call explicitly indicated no errors, ensuring no silent failures occurred.
- ✅ **Error Handling**: The tool call did not produce any errors, as indicated by isError=False.
</details>

#### Step 15: structuredContent

<details>
<summary>Toggle step details</summary>

Score (🤖): 0/6

[→ View tool details](#tool-structuredContent)

**Purpose (🤖):** Testing with an empty location ensures the tool handles invalid inputs gracefully.

**Tool Call (🤖):**
```json
{
  "location": ""
}
```
**Expected (🤖):** The tool should return an error indicating the location is invalid.

**Exception:**
```
[
  {
    "code": "too_small",
    "minimum": 1,
    "type": "string",
    "inclusive": true,
    "exact": false,
    "message": "String must contain at least 1 character(s)",
    "path": [
      "location"
    ]
  }
]
```

**Evaluation (🤖):**
- ❌ **Meets Expectations**: The tool did not meet expectations as it failed to handle the invalid input appropriately and did not return the expected error.
- ❌ **Output Quality**: No output was provided, so the quality of the output cannot be assessed.
- ❌ **Output Relevance**: The output was irrelevant as no response was provided, which does not align with the expected behavior of returning an error.
- ❌ **Schema Compliance**: The tool did not return any output, which violates the expected schema for error handling.
- Bad Request **Error Type**: The invalid location parameter should have triggered a 'Bad Request' error, but no error was returned.
- ❌ **No Silent Error**: The tool failed silently by not returning any output or error message.
- ❌ **Error Handling**: The tool did not return an error as expected when provided with an invalid location parameter.
</details>

</details>

## Tools

<details>
<summary>Toggle details</summary>

<a id="tool-echo"></a>
### echo

<details>
<summary>Toggle tool details</summary>

**Description:**
```
Echoes back the input
```
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "message": {
      "type": "string",
      "description": "Message to echo"
    }
  },
  "required": [
    "message"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
**Output Schema:**
_No Output Schema_
</details>

<a id="tool-add"></a>
### add

<details>
<summary>Toggle tool details</summary>

**Description:**
```
Adds two numbers
```
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "a": {
      "type": "number",
      "description": "First number"
    },
    "b": {
      "type": "number",
      "description": "Second number"
    }
  },
  "required": [
    "a",
    "b"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
**Output Schema:**
_No Output Schema_
</details>

<a id="tool-longRunningOperation"></a>
### longRunningOperation

<details>
<summary>Toggle tool details</summary>

**Description:**
```
Demonstrates a long running operation with progress updates
```
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "duration": {
      "type": "number",
      "default": 10,
      "description": "Duration of the operation in seconds"
    },
    "steps": {
      "type": "number",
      "default": 5,
      "description": "Number of steps in the operation"
    }
  },
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
**Output Schema:**
_No Output Schema_
</details>

<a id="tool-printEnv"></a>
### printEnv

<details>
<summary>Toggle tool details</summary>

**Description:**
```
Prints all environment variables, helpful for debugging MCP server configuration
```
**Input Schema:**
```json
{
  "type": "object",
  "properties": {},
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
**Output Schema:**
_No Output Schema_
</details>

<a id="tool-sampleLLM"></a>
### sampleLLM

<details>
<summary>Toggle tool details</summary>

**Description:**
```
Samples from an LLM using MCP's sampling feature
```
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "prompt": {
      "type": "string",
      "description": "The prompt to send to the LLM"
    },
    "maxTokens": {
      "type": "number",
      "default": 100,
      "description": "Maximum number of tokens to generate"
    }
  },
  "required": [
    "prompt"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
**Output Schema:**
_No Output Schema_
</details>

<a id="tool-getTinyImage"></a>
### getTinyImage

<details>
<summary>Toggle tool details</summary>

**Description:**
```
Returns the MCP_TINY_IMAGE
```
**Input Schema:**
```json
{
  "type": "object",
  "properties": {},
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
**Output Schema:**
_No Output Schema_
</details>

<a id="tool-annotatedMessage"></a>
### annotatedMessage

<details>
<summary>Toggle tool details</summary>

**Description:**
```
Demonstrates how annotations can be used to provide metadata about content
```
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "messageType": {
      "type": "string",
      "enum": [
        "error",
        "success",
        "debug"
      ],
      "description": "Type of message to demonstrate different annotation patterns"
    },
    "includeImage": {
      "type": "boolean",
      "default": false,
      "description": "Whether to include an example image"
    }
  },
  "required": [
    "messageType"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
**Output Schema:**
_No Output Schema_
</details>

<a id="tool-getResourceReference"></a>
### getResourceReference

<details>
<summary>Toggle tool details</summary>

**Description:**
```
Returns a resource reference that can be used by MCP clients
```
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "resourceId": {
      "type": "number",
      "minimum": 1,
      "maximum": 100,
      "description": "ID of the resource to reference (1-100)"
    }
  },
  "required": [
    "resourceId"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
**Output Schema:**
_No Output Schema_
</details>

<a id="tool-startElicitation"></a>
### startElicitation

<details>
<summary>Toggle tool details</summary>

**Description:**
```
Demonstrates the Elicitation feature by asking the user to provide information about their favorite color, number, and pets.
```
**Input Schema:**
```json
{
  "type": "object",
  "properties": {},
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
**Output Schema:**
_No Output Schema_
</details>

<a id="tool-getResourceLinks"></a>
### getResourceLinks

<details>
<summary>Toggle tool details</summary>

**Description:**
```
Returns multiple resource links that reference different types of resources
```
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "count": {
      "type": "number",
      "minimum": 1,
      "maximum": 10,
      "default": 3,
      "description": "Number of resource links to return (1-10)"
    }
  },
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
**Output Schema:**
_No Output Schema_
</details>

<a id="tool-structuredContent"></a>
### structuredContent

<details>
<summary>Toggle tool details</summary>

**Description:**
```
Returns structured content along with an output schema for client data validation
```
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "location": {
      "type": "string",
      "minLength": 1,
      "description": "City name or zip code"
    }
  },
  "required": [
    "location"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "temperature": {
      "type": "number",
      "description": "Temperature in celsius"
    },
    "conditions": {
      "type": "string",
      "description": "Weather conditions description"
    },
    "humidity": {
      "type": "number",
      "description": "Humidity percentage"
    }
  },
  "required": [
    "temperature",
    "conditions",
    "humidity"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```
</details>

</details>

## Resources

<details>
<summary>Toggle details</summary>

<a id="resource-Resource 1"></a>
### Resource 1

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/1`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 2"></a>
### Resource 2

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/2`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 3"></a>
### Resource 3

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/3`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 4"></a>
### Resource 4

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/4`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 5"></a>
### Resource 5

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/5`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 6"></a>
### Resource 6

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/6`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 7"></a>
### Resource 7

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/7`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 8"></a>
### Resource 8

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/8`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 9"></a>
### Resource 9

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/9`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 10"></a>
### Resource 10

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/10`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 11"></a>
### Resource 11

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/11`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 12"></a>
### Resource 12

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/12`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 13"></a>
### Resource 13

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/13`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 14"></a>
### Resource 14

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/14`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 15"></a>
### Resource 15

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/15`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 16"></a>
### Resource 16

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/16`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 17"></a>
### Resource 17

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/17`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 18"></a>
### Resource 18

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/18`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 19"></a>
### Resource 19

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/19`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 20"></a>
### Resource 20

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/20`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 21"></a>
### Resource 21

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/21`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 22"></a>
### Resource 22

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/22`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 23"></a>
### Resource 23

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/23`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 24"></a>
### Resource 24

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/24`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 25"></a>
### Resource 25

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/25`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 26"></a>
### Resource 26

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/26`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 27"></a>
### Resource 27

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/27`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 28"></a>
### Resource 28

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/28`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 29"></a>
### Resource 29

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/29`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 30"></a>
### Resource 30

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/30`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 31"></a>
### Resource 31

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/31`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 32"></a>
### Resource 32

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/32`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 33"></a>
### Resource 33

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/33`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 34"></a>
### Resource 34

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/34`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 35"></a>
### Resource 35

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/35`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 36"></a>
### Resource 36

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/36`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 37"></a>
### Resource 37

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/37`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 38"></a>
### Resource 38

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/38`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 39"></a>
### Resource 39

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/39`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 40"></a>
### Resource 40

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/40`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 41"></a>
### Resource 41

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/41`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 42"></a>
### Resource 42

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/42`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 43"></a>
### Resource 43

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/43`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 44"></a>
### Resource 44

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/44`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 45"></a>
### Resource 45

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/45`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 46"></a>
### Resource 46

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/46`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 47"></a>
### Resource 47

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/47`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 48"></a>
### Resource 48

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/48`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 49"></a>
### Resource 49

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/49`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 50"></a>
### Resource 50

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/50`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 51"></a>
### Resource 51

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/51`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 52"></a>
### Resource 52

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/52`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 53"></a>
### Resource 53

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/53`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 54"></a>
### Resource 54

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/54`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 55"></a>
### Resource 55

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/55`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 56"></a>
### Resource 56

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/56`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 57"></a>
### Resource 57

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/57`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 58"></a>
### Resource 58

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/58`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 59"></a>
### Resource 59

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/59`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 60"></a>
### Resource 60

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/60`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 61"></a>
### Resource 61

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/61`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 62"></a>
### Resource 62

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/62`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 63"></a>
### Resource 63

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/63`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 64"></a>
### Resource 64

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/64`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 65"></a>
### Resource 65

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/65`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 66"></a>
### Resource 66

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/66`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 67"></a>
### Resource 67

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/67`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 68"></a>
### Resource 68

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/68`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 69"></a>
### Resource 69

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/69`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 70"></a>
### Resource 70

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/70`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 71"></a>
### Resource 71

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/71`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 72"></a>
### Resource 72

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/72`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 73"></a>
### Resource 73

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/73`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 74"></a>
### Resource 74

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/74`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 75"></a>
### Resource 75

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/75`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 76"></a>
### Resource 76

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/76`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 77"></a>
### Resource 77

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/77`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 78"></a>
### Resource 78

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/78`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 79"></a>
### Resource 79

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/79`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 80"></a>
### Resource 80

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/80`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 81"></a>
### Resource 81

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/81`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 82"></a>
### Resource 82

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/82`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 83"></a>
### Resource 83

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/83`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 84"></a>
### Resource 84

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/84`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 85"></a>
### Resource 85

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/85`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 86"></a>
### Resource 86

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/86`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 87"></a>
### Resource 87

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/87`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 88"></a>
### Resource 88

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/88`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 89"></a>
### Resource 89

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/89`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 90"></a>
### Resource 90

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/90`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 91"></a>
### Resource 91

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/91`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 92"></a>
### Resource 92

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/92`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 93"></a>
### Resource 93

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/93`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 94"></a>
### Resource 94

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/94`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 95"></a>
### Resource 95

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/95`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 96"></a>
### Resource 96

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/96`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 97"></a>
### Resource 97

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/97`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 98"></a>
### Resource 98

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/98`

**MIME Type:** application/octet-stream

</details>

<a id="resource-Resource 99"></a>
### Resource 99

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/99`

**MIME Type:** text/plain

</details>

<a id="resource-Resource 100"></a>
### Resource 100

<details>
<summary>Toggle resource details</summary>

**URI:** `test://static/resource/100`

**MIME Type:** application/octet-stream

</details>

</details>

## Resource Templates

<details>
<summary>Toggle details</summary>

<a id="resource-template-Static Resource"></a>
### Static Resource

<details>
<summary>Toggle template details</summary>

**URI Template:** `test://static/resource/{id}`

**Description:** A static resource with a numeric ID

</details>

</details>

## Available Prompts

<details>
<summary>Toggle details</summary>

<a id="prompt-simple_prompt"></a>
### simple_prompt

<details>
<summary>Toggle prompt details</summary>

**Description:** A prompt without arguments

</details>

<a id="prompt-complex_prompt"></a>
### complex_prompt

<details>
<summary>Toggle prompt details</summary>

**Description:** A prompt with arguments

**Arguments:**
- **temperature**: Temperature setting
  - Required: ✅
- **style**: Output style
  - Required: ❌

</details>

<a id="prompt-resource_prompt"></a>
### resource_prompt

<details>
<summary>Toggle prompt details</summary>

**Description:** A prompt that includes an embedded resource reference

**Arguments:**
- **resourceId**: Resource ID to include (1-100)
  - Required: ✅

</details>

</details>

## Legend

- ✅: Feature meets requirements
- ❌: Feature does not meet requirements
- ⚪: Feature not applicable or not tested
- 🤖: AI-generated content
