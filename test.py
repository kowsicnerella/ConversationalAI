from mem0_config import memory_agent


messages = [
    {"role": "user", "content": "I love Italian food with indian spice."},
    {"role": "assistant", "content": "Got it! I'll remember that you enjoy Italian cuisine."}
]
memory_agent.add(messages, user_id="alex")

query = "What kind of food does Alex like?"
filters = {"AND": [{"user_id": "alex"}]}
results = memory_agent.search(query, user_id = "alex")
print(results)


# all_memories = memory_agent.get_all(user_id="alex")
# print(all_memories)

# memory_agent.update(memory_id="your-memory-id")

# related_memories = memory_agent.search(query="what food do i like?", user_id="alex")
# print(related_memories)

# memory_agent.delete(memory_id="56e9032a-699d-4c4b-aaf8-4076476a8c08")
