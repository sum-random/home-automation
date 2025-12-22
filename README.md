This code is my home automation project and self learning platform.  It turns my lights on and off each evening, manages my picture collection, keeps my bookmark links handy, and will play audio files in the future.  

Installation Instructions
Starting from a newly installed FreeBSD 14 instance, install the following packages:
apache24 bind916 bottlerocket mariadb mpg123 python311 ap24-py311-mod_wsgi py311-Babel py311-Jinja2 py311-asgiref py311-blinker py311-brotli py311-cairo py311-certifi py311-charset-normalizer py311-click py311-dbus py311-evdev py311-flask py311-idna py311-itsdangerous py311-libevdev py311-markupsafe py311-mutagen py311-olefile py311-packaging py311-pillow py311-pip py311-pycryptodomex py311-pygobject py311-pymysql py311-pysocks py311-python-dotenv py311-pyudev py311-requests py311-setuptools py311-six py311-tkinter py311-urllib3 py311-websockets py311-werkzeug

Apache configuration:
LoadModule wsgi_module libexec/apache24/mod_wsgi.so
WSGIScriptAlias / /usr/local/www/apache24/wsgi-bin/__init__.py
WSGIPythonPath "/usr/local/www/apache24/wsgi-bin:/usr/local/www/apache24/wsgi-lib"
<Directory "/usr/local/www/apache24/wsgi-bin">
    AllowOverride Limit AuthConfig
    # insert your auth schema here
    Options ExecCGI
    SetHandler wsgi-script
    WSGICallableObject app
    <LimitExcept GET>
        Require valid-user
    </LimitExcept>
</Directory>

Deploying code:
Crontab setup:

3. Usage Guide
Walk users through how to use your project. Include code examples, API endpoints, and any configuration they need to know.

4. Configuration
If your project has configurable options, explain them here. This is where users can customize your project to their needs.

5. Contributing Guidelines
Detail how others can contribute to your project. Include information about issues, pull requests, and coding standards.

MIT License

Copyright (c) 2024 Clayton Tucker

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

