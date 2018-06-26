# Auklet Python Agent
[![Maintainability](https://api.codeclimate.com/v1/badges/7c2cd3bc63a70ac7fd73/maintainability)](https://codeclimate.com/repos/5a54e10be3d6cb4d7d0007a8/maintainability)    [![Test Coverage](https://api.codeclimate.com/v1/badges/7c2cd3bc63a70ac7fd73/test_coverage)](https://codeclimate.com/repos/5a54e10be3d6cb4d7d0007a8/test_coverage)  


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
