import os
import sys
import json

# from src.command_parser import (
#     PunctuationParser,
#     ChatGPTParser
# )

# from src.command_executor import (
#     Executor
# )

from src.scheduler.fifo_scheduler import FIFOScheduler

from src.utils.utils import (
    parse_global_args,
    logger
)

from src.agents.agent_factory import AgentFactory

import warnings

from src.llms import llms

from src.agents.math_agent.math_agent import MathAgent

from src.agents.narrative_agent.narrative_agent import NarrativeAgent

from src.agents.rec_agent.rec_agent import RecAgent

from src.agents.travel_agent.travel_agent import TravelAgent

from concurrent.futures import ThreadPoolExecutor, as_completed

def main():
    warnings.filterwarnings("ignore")
    parser = parse_global_args()
    args = parser.parse_args()

    llm_name = args.llm_name
    max_gpu_memory = args.max_gpu_memory
    max_new_tokens = args.max_new_tokens

    llm = llms.LLMKernel(llm_name, max_gpu_memory, max_new_tokens)

    # start the scheduler
    scheduler = FIFOScheduler(llm)
    scheduler.start()

    agent_factory = AgentFactory(
        llm = llm,
        agent_process_queue = scheduler.agent_process_queue
    )

    # assign maximum number of agents that can run in parallel
    agent_thread_pool = ThreadPoolExecutor(max_workers=64)

    # construct agents
    math_agent = agent_factory.activate_agent(
        agent_name = "MathAgent", 
        task_input = "Solve the problem that Albert is wondering how much pizza he can eat in one day. He buys 2 large pizzas and 2 small pizzas. A large pizza has 16 slices and a small pizza has 8 slices. If he eats it all, how many pieces does he eat that day?",
    )

    narrative_agent = agent_factory.activate_agent(
        agent_name = "NarrativeAgent", 
        task_input = "Craft a tale about a valiant warrior on a quest to uncover priceless treasures hidden within a mystical island.",
    )
    
    rec_agent = agent_factory.activate_agent(
        agent_name = "RecAgent", 
        task_input = "I want to take a tour to New York during the spring break, recommend some restaurants around for me.",
    )
    agents = [math_agent, narrative_agent, rec_agent]

    # run agents concurrently
    tasks = [agent_thread_pool.submit(agent.run) for agent in agents]

    for r in as_completed(tasks):
        res = r.result()
        # logger.info(res)

    scheduler.stop()

if __name__ == "__main__":
    main()
