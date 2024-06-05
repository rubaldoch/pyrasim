#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
from src.processor.sfcw_signal_processor_sim import SfcwSimulationConfig, sfcw_signal_processor


if __name__ == "__main__":

    # Bandwith constante, N variable

    # for i in range(5, 55, 5):
    #     config = SfcwSimulationConfig(
    #         name=f"bandwidth-constante-{i}",
    #         start_frequency=100e6,
    #         end_frequency=250e6,
    #         N = i,
    #         )
    #     ensayo = {}
    #     ensayo['config'] = config.__dict__
    #     print(ensayo)
    #     ensayo['results'] =  sfcw_signal_processor(config)
    #     file_ensayo = open(f"{config.name}.json", "w")
    #     file_ensayo.write(json.dumps(ensayo))
    #     file_ensayo.close()

    for i in range(120, 200, 20):
        config = SfcwSimulationConfig(
            name=f"freq-step-constante-{i}",
            start_frequency=100e6,
            step_frequency=3e6,
            N = i,
            )
        ensayo = {}
        ensayo['config'] = config.__dict__
        print(ensayo)
        ensayo['results'] =  sfcw_signal_processor(config)
        file_ensayo = open(f"{config.name}.json", "w")
        file_ensayo.write(json.dumps(ensayo))
        file_ensayo.close()

    # for i in range(1, 6, 1):
    #     config = SfcwSimulationConfig(
    #         name=f"freq-inicial-variable-N50-{i}",
    #         start_frequency=(2**i)*100e6,
    #         step_frequency=3e6,
    #         N = 50,
    #         )
    #     ensayo = {}
    #     ensayo['config'] = config.__dict__
    #     print(ensayo)
    #     ensayo['results'] =  sfcw_signal_processor(config)
    #     file_ensayo = open(f"{config.name}.json", "w")
    #     file_ensayo.write(json.dumps(ensayo))
    #     file_ensayo.close()

    # for i in range(1, 6, 1):
    #     config = SfcwSimulationConfig(
    #         name=f"freq-inicial-variable-N100-{i}",
    #         start_frequency=(2**i)*100e6,
    #         step_frequency=3e6,
    #         N = 50,
    #         )
    #     ensayo = {}
    #     ensayo['config'] = config.__dict__
    #     print(ensayo)
    #     ensayo['results'] =  sfcw_signal_processor(config)
    #     file_ensayo = open(f"{config.name}.json", "w")
    #     file_ensayo.write(json.dumps(ensayo))
    #     file_ensayo.close()