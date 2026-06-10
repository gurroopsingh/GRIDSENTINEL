"""GRIDSENTINEL — Self-Healing Action Executor"""

import copy
import numpy as np
from simulation.grid_model import run_powerflow


def execute_healing(net, city_buses: dict, diagnosis: dict) -> dict:
    """Execute autonomous self-healing. Returns actions taken + success."""
    healed_net = copy.deepcopy(net)
    actions_taken = []

    # Strategy 1: Re-enable backup lines
    disabled_lines = healed_net.line[~healed_net.line["in_service"]]
    for idx in disabled_lines.index:
        test_net = copy.deepcopy(healed_net)
        test_net.line.loc[idx, "in_service"] = True
        if run_powerflow(test_net):
            if test_net.res_line["loading_percent"].max() < 100:
                healed_net = test_net
                actions_taken.append({
                    "strategy": "line_switching",
                    "action": f"Re-enabled {healed_net.line.loc[idx, 'name']}",
                    "component": healed_net.line.loc[idx, "name"],
                    "reasoning": "Line re-enabled safely within limits",
                })

    # Strategy 2: Generator redispatch
    if not run_powerflow(healed_net):
        for idx in healed_net.sgen.index:
            if healed_net.sgen.loc[idx, "in_service"]:
                healed_net.sgen.loc[idx, "p_mw"] *= 1.15
                actions_taken.append({
                    "strategy": "generator_redispatch",
                    "action": f"Boosted {healed_net.sgen.loc[idx, 'name']} +15%",
                    "component": healed_net.sgen.loc[idx, "name"],
                    "reasoning": "Compensating for lost capacity",
                })

    # Strategy 3: Load shedding (last resort)
    if not run_powerflow(healed_net):
        load_indices = healed_net.load.index.tolist()
        for idx in load_indices[-max(1, len(load_indices)//5):]:
            orig = healed_net.load.loc[idx, "p_mw"]
            healed_net.load.loc[idx, "p_mw"] *= 0.5
            actions_taken.append({
                "strategy": "load_shedding",
                "action": f"Shed 50% of {healed_net.load.loc[idx, 'name']}",
                "component": healed_net.load.loc[idx, "name"],
                "reasoning": f"Emergency shed {orig*0.5:.1f} MW to prevent cascade",
            })

    final_success = run_powerflow(healed_net)
    return {
        "success": final_success,
        "actions_taken": actions_taken,
        "strategies_used": list(set(a["strategy"] for a in actions_taken)),
        "total_actions": len(actions_taken),
    }
