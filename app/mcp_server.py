"""MCP Server for Universal Credit Calculator."""
import json
import logging
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult
import asyncio

from app.utils.uc_calculator import UCCalculator
from app.utils.lha_service import LHAService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uc-calculator-mcp")


class UCCalculatorMCPServer:
    """MCP Server for Universal Credit calculations."""

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("Universal Credit Calculator")
        self.calculator = UCCalculator()
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Set up MCP tools."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="calculate_uc",
                    description="Calculate Universal Credit entitlement based on claimant circumstances",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "claimant_type": {
                                "type": "string",
                                "enum": ["single", "joint"],
                                "description": "Type of claim",
                            },
                            "claimant_age": {
                                "type": "integer",
                                "description": "Age of main claimant",
                            },
                            "partner_age": {
                                "type": "integer",
                                "description": "Age of partner (for joint claims)",
                            },
                            "num_children": {
                                "type": "integer",
                                "description": "Number of children (0-20)",
                                "default": 0,
                            },
                            "children_ages": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Ages of children if applicable",
                            },
                            "monthly_earnings": {
                                "type": "number",
                                "description": "Claimant's net monthly earnings",
                                "default": 0,
                            },
                            "partner_monthly_earnings": {
                                "type": "number",
                                "description": "Partner's net monthly earnings",
                                "default": 0,
                            },
                            "monthly_rent": {
                                "type": "number",
                                "description": "Monthly rent paid",
                            },
                            "brma_code": {
                                "type": "string",
                                "description": "Broad Rental Market Area code for LHA lookup",
                            },
                            "bedrooms_needed": {
                                "type": "integer",
                                "description": "Number of bedrooms needed",
                                "default": 1,
                            },
                            "has_work_allowance": {
                                "type": "boolean",
                                "description": "Whether claimant has work allowance",
                                "default": False,
                            },
                            "has_childcare_costs": {
                                "type": "boolean",
                                "description": "Whether claimant has childcare costs",
                                "default": False,
                            },
                            "monthly_childcare_costs": {
                                "type": "number",
                                "description": "Monthly childcare costs",
                                "default": 0,
                            },
                            "has_disability": {
                                "type": "boolean",
                                "description": "Whether claimant has disability",
                                "default": False,
                            },
                            "is_carer": {
                                "type": "boolean",
                                "description": "Whether claimant is a carer",
                                "default": False,
                            },
                        },
                        "required": [
                            "claimant_type",
                            "claimant_age",
                            "monthly_rent",
                        ],
                    },
                ),
                Tool(
                    name="get_lha_rate",
                    description="Get Local Housing Allowance rate for a BRMA",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "brma_code": {
                                "type": "string",
                                "description": "Broad Rental Market Area code",
                            },
                            "bedrooms": {
                                "type": "integer",
                                "description": "Number of bedrooms",
                                "default": 1,
                            },
                        },
                        "required": ["brma_code"],
                    },
                ),
                Tool(
                    name="list_lha_rates",
                    description="List all LHA rates for a BRMA",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "brma_code": {
                                "type": "string",
                                "description": "Broad Rental Market Area code",
                            },
                        },
                        "required": ["brma_code"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> ToolResult:
            """Handle tool calls."""
            try:
                if name == "calculate_uc":
                    return await self._handle_calculate_uc(arguments)
                elif name == "get_lha_rate":
                    return await self._handle_get_lha_rate(arguments)
                elif name == "list_lha_rates":
                    return await self._handle_list_lha_rates(arguments)
                else:
                    return ToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Unknown tool: {name}",
                            )
                        ],
                        isError=True,
                    )
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return ToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True,
                )

    async def _handle_calculate_uc(self, arguments: dict) -> ToolResult:
        """Handle UC calculation request."""
        # Parse children data
        num_children = arguments.get("num_children", 0)
        children = []
        if num_children > 0:
            children_ages = arguments.get("children_ages", [])
            for age in children_ages[:num_children]:
                children.append({"age": age, "is_disabled": False})

        # Get LHA rate if BRMA provided
        lha_rate = None
        if arguments.get("brma_code"):
            lha_rate = LHAService.get_lha_rate(
                arguments["brma_code"],
                arguments.get("bedrooms_needed", 1),
            )

        # Calculate
        result = self.calculator.calculate(
            claimant_type=arguments["claimant_type"],
            claimant_age=arguments["claimant_age"],
            partner_age=arguments.get("partner_age"),
            children=children,
            monthly_earnings=arguments.get("monthly_earnings", 0),
            partner_monthly_earnings=arguments.get("partner_monthly_earnings", 0),
            monthly_rent=arguments["monthly_rent"],
            lha_rate=lha_rate,
            has_work_allowance=arguments.get("has_work_allowance", False),
            monthly_childcare_costs=arguments.get("monthly_childcare_costs", 0),
            has_disability=arguments.get("has_disability", False),
            is_carer=arguments.get("is_carer", False),
        )

        return ToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2),
                )
            ]
        )

    async def _handle_get_lha_rate(self, arguments: dict) -> ToolResult:
        """Handle LHA rate lookup."""
        brma_code = arguments["brma_code"]
        bedrooms = arguments.get("bedrooms", 1)

        rate = LHAService.get_lha_rate(brma_code, bedrooms)
        if rate is None:
            return ToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"LHA rate not found for BRMA {brma_code} with {bedrooms} bedroom(s)",
                    )
                ],
                isError=True,
            )

        return ToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps({
                        "brma_code": brma_code,
                        "bedrooms": bedrooms,
                        "monthly_rate": rate,
                    }, indent=2),
                )
            ]
        )

    async def _handle_list_lha_rates(self, arguments: dict) -> ToolResult:
        """Handle listing all LHA rates for a BRMA."""
        brma_code = arguments["brma_code"]
        rates = LHAService.get_lha_rates_for_brma(brma_code)

        if rates is None:
            return ToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"BRMA {brma_code} not found",
                    )
                ],
                isError=True,
            )

        return ToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps({
                        "brma_code": brma_code,
                        "rates": rates,
                    }, indent=2),
                )
            ]
        )

    async def run(self) -> None:
        """Run the MCP server."""
        async with self.server:
            logger.info("Universal Credit Calculator MCP Server started")
            await self.server.wait_for_shutdown()


def create_mcp_server() -> UCCalculatorMCPServer:
    """Create and return the MCP server."""
    return UCCalculatorMCPServer()
