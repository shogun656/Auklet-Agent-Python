# Auklet Python Agent

Auklet's IoT Python Monitoring agent is built to run in both python 2.x and 3.x.

# Installation

To install the agent:

	pip install auklet


# Usage

To setup Auklet monitoring for you application:

    from auklet.monitoring import Monitoring
    auklet_monitoring = Monitoring("api_key", "app_id")

    auklet_monitoring.start()
    # Call your main function
    main()
    auklet_monitoring.stop()
