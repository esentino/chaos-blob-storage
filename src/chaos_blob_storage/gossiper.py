"""
Gossiper app hold information about all connected node and is responsible for exchange information
on changes in changes of nodes.
- Each node send heartbeat information to gossiper (I'm still alive and kicking)
- Gossiper distribute that information to rest of node of changes
- Gossiper remove node from list if node don't response
"""
