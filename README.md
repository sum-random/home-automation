This code is my home automation project and self learning platform.  It turns my lights on and off each evening, manages my picture collection, keeps my bookmark links handy, and will play audio files in the future.  

Installation Instructions
Starting from a newly installed FreeBSD 12 instance, install the following packages:
apache24 ap24-py39-mod_wsgi bind916 bottlerocket mariadb or mysql mpg123 python39 py39-pip
Install PIP packages:
Flask Pillow pymysql-pool
Apache configuration:
Deploying code:
Crontab setup:

3. Usage Guide
Walk users through how to use your project. Include code examples, API endpoints, and any configuration they need to know.

4. Configuration
If your project has configurable options, explain them here. This is where users can customize your project to their needs.

5. Contributing Guidelines
Detail how others can contribute to your project. Include information about issues, pull requests, and coding standards.

MIT License

Copyright (c) 2023 Clayton Tucker

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

