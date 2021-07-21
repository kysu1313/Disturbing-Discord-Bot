#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "9e83f3e0-fdb1-4e73-a26e-2fb7aa0e9f9e")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "kysu-3376")
