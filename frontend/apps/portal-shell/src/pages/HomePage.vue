<template>
  <main class="blog-home">
    <header class="blog-nav">
      <router-link to="/" class="brand">
        <span class="logo-mark">路</span>
        <span>路那 fun</span>
      </router-link>
      <nav>
        <a>首页</a>
        <a>随笔</a>
        <a>书单</a>
        <a>关于</a>
        <router-link to="/systems">系统</router-link>
      </nav>
    </header>

    <section class="blog-hero">
      <div class="hero-copy">
        <p class="blog-eyebrow">PERSONAL BLOG</p>
        <h1>路那 fun</h1>
        <p class="blog-intro">
          一个准备慢慢长出来的个人博客。记录生活里的小事、阅读笔记、代码学习，
          还有偶尔冒出来的有趣想法。
        </p>
        <div class="blog-actions">
          <span class="black-button">看看最近</span>
          <span class="ghost-button">关于我</span>
        </div>
      </div>

      <div class="note-window">
        <div class="window-shadow"></div>
        <article class="window-card">
          <div class="window-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <div class="paper-lines">
            <p class="date">TUESDAY / 04.21</p>
            <h2>晴天备忘录</h2>
            <p>
              今天先把网站搭成一个安静的小角落。页面不用很满，但每次打开都能想起要好好生活。
            </p>
            <div class="pill-row">
              <span>生活</span>
              <span>灵感</span>
              <span>博客</span>
            </div>
            <i class="circle red"></i>
            <i class="circle yellow"></i>
          </div>
        </article>
      </div>
    </section>

    <section class="latest-section">
      <div class="latest-head">
        <p class="blog-eyebrow">LATEST NOTES</p>
        <h2>最近更新</h2>
      </div>
      <div class="note-grid">
        <article v-for="note in notes" :key="note.title" class="note-card">
          <div>
            <span>{{ note.date }}</span>
            <span>{{ note.tag }}</span>
          </div>
          <h3>{{ note.title }}</h3>
          <p>{{ note.text }}</p>
        </article>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
const notes = [
  {
    date: "04.21",
    tag: "日记",
    title: "把今天写成一小段",
    text: "日常、灵感和一些正在路上的想法，先慢慢收进这里。",
  },
  {
    date: "04.18",
    tag: "阅读",
    title: "最近读到的好句子",
    text: "留一点空白给阅读，也留一点时间给自己重新出发。",
  },
  {
    date: "04.12",
    tag: "随笔",
    title: "一个博客的开始",
    text: "不用太复杂，先有一个舒服的地方，之后再一点点变完整。",
  },
]
</script>
