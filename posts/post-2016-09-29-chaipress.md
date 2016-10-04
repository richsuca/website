title: Chaipress
name: chaipress
date: 2016-09-29 19:00:00
text:
On a September 1st afternoon, I found an article about [Linux kernel GPL enforcement][1] on [Hacker News][2]. It referenced Torvald's [reply][3] on the thread. I read it and enjoyed the argument made and the style it was made in. It also got me curious about plain text formatting (`*bold*`, `_underscore_`,  `[footnotes]`, `> for quoting`). I suddenly had a desire to write like that and wondered if there was a blogging service that supported that. My website _was_ on WordPress and it could work using `<pre>` Html tag but plain text wasn't *the* only way to write.

So I Googled for "plain text blog" and found <http://calepin.co/> and it was nice but not exactly what I was looking for. I noticed the words "Powered by Pelican" in the footer. That got me looking up [Pelican](http://docs.getpelican.com/) and I learnt it was a "static site generator written in Python". Interesting<sup>1</sup>. On the same Google results page, there was a blog post about [building a static blog with Pelican][4]. The post describes blogging options and makes an argument for static site generators. It also provides step-by-step instructions to get Pelican working, but the most useful paragraph for me was

  > The hosting resources required for public deployment are very small, 
  > allowing one to use very cheap hosts such as NearlyFreeSpeech. Outside the domain registration costs, 
  > the running costs come to less than $1 per month, which is a great saving!
  
[NearlyFreeSpeech][5] was the final<sup>3</sup> ingredient needed to make [Chaipress][6] - my own static site generator. I don't know if it was the geekiness of NearlyFreeSpeech's website, their philosophy, or the pricing but it got me started and I had the first generated website up on September 17th. Writing the generator didn't take long but importing my WordPress posts did<sup>2</sup>. And I forgot about the plain text *only* thing that started all this.

I called it Chaipress because Chai(tea) is simple, easy-to-make, low cost, and refreshing. The _press_ is a suffix borrowed from the names of other blogging systems (WordPress, Octopress).

[1]: http://lwn.net/Articles/698452/
[2]: https://news.ycombinator.com
[3]: https://lists.linuxfoundation.org/pipermail/ksummit-discuss/2016-August/003580.html
[4]: https://www.notionsandnotes.org/tech/web-development/pelican-static-blog-setup.html
[5]: https://www.nearlyfreespeech.net/
[6]: https://github.com/richsuca/chaipress

<small>
Footnotes:

1. Python is my favourite and Blogging apps are an eternal curiosity of mine. I did try Pelican. 
2. Text encoding mistakes. WordPress posts were not in Html so I had to convert them using Markdown. In hindsight, I could have left it as-is and converted them during page generation instead.
3. My previous attempts at writing my own blog engine went nowhere. When I started working as a programmer, blogging was _a thing_ and writing a blog engine was also _a thing_. [It][7] [still][8] [is][9].

</small>
[7]: https://news.ycombinator.com/item?id=10491873
[8]: http://www.staticgen.com/
[9]: https://github.com/search?utf8=%E2%9C%93&q=blog
