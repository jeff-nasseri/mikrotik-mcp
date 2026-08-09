# MikroTik MCP - Learning Resources & Examples

Welcome to the MikroTik MCP (Model Context Protocol) learning hub! This repository contains comprehensive resources, practical examples, and tutorials to help network engineers and developers leverage AI-powered network management with MikroTik devices.

## 📚 What is MikroTik MCP?

MikroTik MCP is an AI-powered interface that allows you to manage and configure MikroTik RouterOS devices using natural language commands. Instead of memorizing complex CLI syntax, you can simply describe what you want to accomplish, and the AI assistant will execute the appropriate MikroTik commands through the MCP tools.

## 📖 Learning Resources

### Articles & Tutorials

#### Medium
1. **[Bringing AI-Powered Network Management to Network Engineers](https://medium.com/@sir.jeff.nasseri/bringing-ai-powered-network-management-to-network-engineers-06167aab409f)**  
   *Author: [@jeff-nasseri](https://medium.com/@sir.jeff.nasseri)*  
   An introductory guide exploring how AI transforms traditional network management workflows, with practical examples using MikroTik MCP.

2. **[Managing a Whole MikroTik Fleet from One MCP Server](https://medium.com/@sir.jeff.nasseri/managing-a-whole-mikrotik-fleet-from-one-mcp-server-60245de07073)**  
   *Author: [@jeff-nasseri](https://medium.com/@sir.jeff.nasseri)*  
   How to manage multiple MikroTik devices from a single MCP server using the inventory: configuring the YAML file, wiring it up (including Docker), and prompt patterns for fleet work. Also available [in this repository](managing-a-mikrotik-fleet.md).

### Example Workflow

```
You: "Create a guest network on VLAN 200 with DHCP"

AI: I'll set up a complete guest network for you:
    - Creates VLAN interface
    - Assigns IP address
    - Configures DHCP server
    - Adds NAT rules
    [Executes MCP tools]
    
Result: Guest network is ready and operational!
```

## 📋 Example Library

We provide **25 comprehensive examples** covering common network scenarios,
including five dedicated to **multi-device (inventory) prompt engineering**:
discovering the fleet, rolling a change out across tagged devices, comparing
configuration between routers, safe-mode-guarded changes on one device of the
fleet, and fleet-wide changes with per-device verification.

[**View All 25 Examples →**](examples.md)
