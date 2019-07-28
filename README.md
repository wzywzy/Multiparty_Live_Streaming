# MultiLive: Adaptive Bitrate Control for Low-delay Multiparty Interactive Live Streaming
MultiLive is a bitrate control algorithm for multi-party streaming architecture.

### Simulator

We build a simulator to evaluate our algorithm over this new scenario in `sim/`. As each part of the architecture is established in `sim/env.py`, and our algorithm is described in `sim/algorithm.py` and `sim/cluster.py`.

### Demo

To test the demo with SJDD traces, in `demo/` run
```
python run.py
``` 

You can also check the usage of our simulator here.

### traces

In our experiments, we use 2 datasets. One is a Belgium 4G network traces in `traces/Belgium`. The other is a network trace dataset collected in 3 live streaming servers. It is collected by a company we collabrate with, which is in `traces/SJDD`.

### Interface

To run over algorithm on real testbed, we make a simplified C++ version which can be build as a library. If you happen to run a similar C/C++ platform, you can test our algorithm with codes in `interface/`.
