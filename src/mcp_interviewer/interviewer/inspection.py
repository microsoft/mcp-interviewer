"""Server inspection functionality."""

import asyncio
import logging

from mcp import ClientSession

from ..models import Server, ServerParameters

logger = logging.getLogger(__name__)


async def inspect_server(server: ServerParameters, session: ClientSession) -> Server:
    """Inspect an MCP server to discover its capabilities and features.

    Initializes the server connection and retrieves all available tools,
    resources, resource templates, and prompts based on the server's
    advertised capabilities.

    Args:
        server: ServerParameters for launching the server
        session: The MCP ClientSession to use for inspection

    Returns:
        Server object containing all discovered features and capabilities
    """
    if server.connection_type == "stdio":
        logger.info(
            f"Starting server inspection for: {server.command} {' '.join(server.args or [])}"
        )
    else:
        logger.info(f"Starting server inspection for: {server.url}")
    logger.debug(f"Server parameters: {server}")

    logger.info("Initializing client session...")
    initialize_result = await session.initialize()
    await asyncio.sleep(0.2)
    logger.info("Client session initialized successfully")
    logger.debug(f"Server capabilities: {initialize_result.capabilities}")
    tools = []
    resources = []
    resource_templates = []
    prompts = []

    if initialize_result.capabilities.tools is not None:
        logger.info("Server supports tools capability - fetching tools")
        try:
            result = await session.list_tools()
            logger.debug(f"Initial tools batch: {len(result.tools)} tools")

            while result.nextCursor:
                tools.extend(result.tools)
                logger.debug(
                    f"Fetching next batch of tools with cursor: {result.nextCursor}"
                )
                result = await session.list_tools(result.nextCursor)
                logger.debug(f"Retrieved {len(result.tools)} more tools")

            tools.extend(result.tools)
            logger.info(f"Successfully fetched {len(tools)} total tools")
            for tool in tools:
                logger.debug(f"Tool found: {tool.name}")
        except Exception as e:
            logger.warning(f"Failed to list tools: {e}", exc_info=True)
    else:
        logger.info("Server does not support tools capability")

    if initialize_result.capabilities.resources is not None:
        logger.info("Server supports resources capability - fetching resources")
        try:
            result = await session.list_resources()
            logger.debug(f"Initial resources batch: {len(result.resources)} resources")

            while result.nextCursor:
                resources.extend(result.resources)
                logger.debug(
                    f"Fetching next batch of resources with cursor: {result.nextCursor}"
                )
                result = await session.list_resources(result.nextCursor)
                logger.debug(f"Retrieved {len(result.resources)} more resources")

            resources.extend(result.resources)
            logger.info(f"Successfully fetched {len(resources)} total resources")
            for resource in resources:
                logger.debug(
                    f"Resource found: {resource.name if hasattr(resource, 'name') else resource}"
                )
        except Exception as e:
            logger.warning(f"Failed to list resources: {e}", exc_info=True)

        logger.info("Fetching resource templates")

        try:
            result = await session.list_resource_templates()
            logger.debug(
                f"Initial resource templates batch: {len(result.resourceTemplates)} templates"
            )

            while result.nextCursor:
                resource_templates.extend(result.resourceTemplates)
                logger.debug(
                    f"Fetching next batch of resource templates with cursor: {result.nextCursor}"
                )
                result = await session.list_resource_templates(result.nextCursor)
                logger.debug(
                    f"Retrieved {len(result.resourceTemplates)} more templates"
                )

            resource_templates.extend(result.resourceTemplates)
            logger.info(
                f"Successfully fetched {len(resource_templates)} total resource templates"
            )
            for template in resource_templates:
                logger.debug(
                    f"Resource template found: {template.name if hasattr(template, 'name') else template}"
                )
        except Exception as e:
            logger.warning(f"Failed to list resource templates: {e}", exc_info=True)
    else:
        logger.info("Server does not support resources capability")

    if initialize_result.capabilities.prompts is not None:
        logger.info("Server supports prompts capability - fetching prompts")
        try:
            result = await session.list_prompts()
            logger.debug(f"Initial prompts batch: {len(result.prompts)} prompts")

            while result.nextCursor:
                prompts.extend(result.prompts)
                logger.debug(
                    f"Fetching next batch of prompts with cursor: {result.nextCursor}"
                )
                result = await session.list_prompts(result.nextCursor)
                logger.debug(f"Retrieved {len(result.prompts)} more prompts")

            prompts.extend(result.prompts)
            logger.info(f"Successfully fetched {len(prompts)} total prompts")
            for prompt in prompts:
                logger.debug(
                    f"Prompt found: {prompt.name if hasattr(prompt, 'name') else prompt}"
                )
        except Exception as e:
            logger.warning(f"Failed to list prompts: {e}", exc_info=True)
    else:
        logger.info("Server does not support prompts capability")

    logger.info("Server inspection completed successfully")
    logger.info(
        f"Server summary: {len(tools)} tools, {len(resources)} resources, "
        f"{len(resource_templates)} resource templates, {len(prompts)} prompts"
    )

    server_obj = Server(
        parameters=server,
        initialize_result=initialize_result,
        tools=tools,
        resources=resources,
        resource_templates=resource_templates,
        prompts=prompts,
    )
    logger.debug(f"Created Server object: {server_obj}")
    return server_obj
