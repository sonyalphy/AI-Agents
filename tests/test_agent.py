from src.agent import Agent, get_default_tools

def test_echo():
    agent = Agent(session={}, tools=get_default_tools())
    reply, used = agent.handle("hello agent")
    assert "You said: hello agent" in reply
    assert used == ["echo"]

def test_calc():
    agent = Agent(session={}, tools=get_default_tools())
    reply, used = agent.handle("add 2 and 3")
    assert "5" in reply
    assert "calculator" in used
