# Auklet Python Agent

Auklet's IoT Python agent is built to run in both python 2.x and 3.x.

# Installation

To install the agent:

	pip install auklet


# Usage

To setup your app to be profiled:

    from auklet.profiler import SamplingProfiler
    samplingProfiler = SamplingProfiler("api_key", "app_id")

    samplingProfiler.start()
    # Call your main function
    main()
    samplingProfiler.stop()
