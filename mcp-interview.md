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

**Date:** 2025-09-02

**mcp-interviewer Version:** [0.0.10](https://github.com/microsoft/mcp-interviewer)

**Evaluation Model:** gpt-4o

#### CLI Command

```bash
mcp-interviewer--model gpt-4o --client trapi.Trapi npx -y @modelcontextprotocol/server-everything
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
## Tool Call Statistics

| Metric | Total | Average | Min | Max |
| --- | --- | --- | --- | --- |
| Tool calls attempted | 15 |  |  |  |
| Tool calls returned output | 12 |  |  |  |
| Tool call outputs with no error | 12 |  |  |  |
| Tool call outputs with error | 0 |  |  |  |
| Exceptions calling tools | 3 |  |  |  |
| Tool call output lengths (gpt-4o text tokens) | 1,168 | 97.3 | 3 | 1,007 |
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

## Functional Test Results

<details>
<summary>Toggle details</summary>


### Test Steps

#### Step 1: echo

<details>
<summary>Toggle step details</summary>

[→ View tool details](#tool-echo)

**Tool Call (🤖):**
```json
{
  "message": "Hello, MCP!"
}
```
**Actual Output (1 blocks):**

```
Echo: Hello, MCP!
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 6 |
| Text blocks | 1 |

</details>

#### Step 2: add

<details>
<summary>Toggle step details</summary>

[→ View tool details](#tool-add)

**Tool Call (🤖):**
```json
{
  "a": 5,
  "b": 10
}
```
**Actual Output (1 blocks):**

```
The sum of 5 and 10 is 15.
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 12 |
| Text blocks | 1 |

</details>

#### Step 3: add

<details>
<summary>Toggle step details</summary>

[→ View tool details](#tool-add)

**Tool Call (🤖):**
```json
{
  "a": -3,
  "b": 7
}
```
**Actual Output (1 blocks):**

```
The sum of -3 and 7 is 4.
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 12 |
| Text blocks | 1 |

</details>

#### Step 4: longRunningOperation

<details>
<summary>Toggle step details</summary>

[→ View tool details](#tool-longRunningOperation)

**Tool Call (🤖):**
```json
{
  "duration": 5,
  "steps": 3
}
```
**Actual Output (1 blocks):**

```
Long running operation completed. Duration: 5 seconds, Steps: 3.
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 16 |
| Text blocks | 1 |

</details>

#### Step 5: printEnv

<details>
<summary>Toggle step details</summary>

[→ View tool details](#tool-printEnv)

**Tool Call (🤖):**
```json
{}
```
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
... (2594 chars truncated)
```
**Output Statistics:**

| Metric | Value |
| --- | --- |
| Text token count | 1,007 |
| Text blocks | 1 |

</details>

#### Step 6: sampleLLM

<details>
<summary>Toggle step details</summary>

[→ View tool details](#tool-sampleLLM)

**Tool Call (🤖):**
```json
{
  "prompt": "What is the capital of France?",
  "maxTokens": 50
}
```
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

</details>

#### Step 7: getTinyImage

<details>
<summary>Toggle step details</summary>

[→ View tool details](#tool-getTinyImage)

**Tool Call (🤖):**
```json
{}
```
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

</details>

#### Step 8: annotatedMessage

<details>
<summary>Toggle step details</summary>

[→ View tool details](#tool-annotatedMessage)

**Tool Call (🤖):**
```json
{
  "messageType": "success",
  "includeImage": true
}
```
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

</details>

#### Step 9: getResourceReference

<details>
<summary>Toggle step details</summary>

[→ View tool details](#tool-getResourceReference)

**Tool Call (🤖):**
```json
{
  "resourceId": 42
}
```
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

</details>

#### Step 10: getResourceReference

<details>
<summary>Toggle step details</summary>

[→ View tool details](#tool-getResourceReference)

**Tool Call (🤖):**
```json
{
  "resourceId": 101
}
```
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

</details>

#### Step 11: startElicitation

<details>
<summary>Toggle step details</summary>

[→ View tool details](#tool-startElicitation)

**Tool Call (🤖):**
```json
{}
```
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

</details>

#### Step 12: getResourceLinks

<details>
<summary>Toggle step details</summary>

[→ View tool details](#tool-getResourceLinks)

**Tool Call (🤖):**
```json
{
  "count": 5
}
```
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

</details>

#### Step 13: getResourceLinks

<details>
<summary>Toggle step details</summary>

[→ View tool details](#tool-getResourceLinks)

**Tool Call (🤖):**
```json
{
  "count": 11
}
```
**Exception:**
```
[
  {
    "code": "too_big",
    "maximum": 10,
    "type": "number",
    "inclusive": true,
    "exact": false,
    "message": "Number must be less than or equal to 10",
    "path": [
      "count"
    ]
  }
]
```

</details>

#### Step 14: structuredContent

<details>
<summary>Toggle step details</summary>

[→ View tool details](#tool-structuredContent)

**Tool Call (🤖):**
```json
{
  "location": "New York"
}
```
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

</details>

#### Step 15: structuredContent

<details>
<summary>Toggle step details</summary>

[→ View tool details](#tool-structuredContent)

**Tool Call (🤖):**
```json
{
  "location": ""
}
```
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
