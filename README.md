## auto_mail_arxiv_filter.py
根据关键词筛选当前[arxiv/astro-ph/new](https://arxiv.org/list/astro-ph/new)网页上的文章，并通过邮件发送结果.
### Usage:
~~~-h --help: <help>
-k --key: <keywords> string A or A,B,C
-u --usr: <mail server username> string A
-p --pwd: <mail server password> string A
-s --snd: <mail sender address> string A
-r --rcv: <mail receiver address> string A or A,B,C

Example: -k Galaxy,AGN -u sdf -p 12345678 -s test@tset.edu.cn -r test@test.edu.cn
~~~
