#!/usr/bin/env python
from app import app
import os
port = os.environ.get('PORT', 5000)
#app.run(debug = True)
app.run(host='0.0.0.0', port=port)