---
layout: default
---

<header class="hero">
  <div class="hero__photo reveal">
    <img
      src="{{ '/assets/img/hero-1400.jpg' | relative_url }}"
      srcset="{{ '/assets/img/hero-700.jpg' | relative_url }} 700w, {{ '/assets/img/hero-1400.jpg' | relative_url }} 1400w"
      sizes="100vw"
      width="1400" height="764"
      alt="Red and blue ink swirling together into violet, suspended in a glass bowl of water"
      loading="eager" fetchpriority="high">
  </div>
  <p class="kicker">A love story, told out loud</p>
  <h1 class="hero__title">DBest In<br>Love</h1>
  <div class="merge-bar" aria-hidden="true"></div>
  <p class="hero__tagline">10 Years Apart · Together Forever</p>
  <p class="hero__hook">
    We met in a comment section nobody remembers — one of us always typing too
    late, the other always reading too early. Ten years, three countries, and
    three years of a pandemic later, we are still choosing each other.
  </p>
</header>

<nav class="links reveal" id="links" aria-label="Find us online">
  {% for link in site.data.links %}
    {% if link.url %}
    <a class="btn btn--{{ link.style }}"
       href="{% include utm.html base=link.url slot='nav' %}"
       {% if link.external %}target="_blank" rel="noopener me"{% endif %}>
    {% else %}
    <div class="btn btn--{{ link.style }}">
    {% endif %}
      <span class="btn__icon">{% include icon.html name=link.icon %}</span>
      <span class="btn__text">
        <strong>{{ link.label }}</strong>
        <small>{{ link.sub }}</small>
      </span>
      {% if link.badge %}
        <span class="pill">{{ link.badge }}</span>
      {% else %}
        <span class="btn__arrow" aria-hidden="true">→</span>
      {% endif %}
    {% if link.url %}</a>{% else %}</div>{% endif %}
  {% endfor %}
</nav>

<section class="story section reveal" id="story">
  <h2 class="section-title">Our Story</h2>

  {%- comment -%}
  Stage 4 (REDESIGN_PLAN): the story spine renders from data — chapters from
  _data/chapters.yml, episodes from _episodes/. The chronology loop lives in
  _includes/story.html and feature-flags itself: zero published episodes ->
  prose-only chapters with "Filming now" placeholders; episode #1 un-drafted ->
  full chapter × episode list + "Start here" pin. No template edit is ever
  required to populate it (ADR-009).
  {%- endcomment -%}
  {% include story.html %}

  <p><a class="text-link" href="{% include utm.html base=site.data.site.tiktok.url slot='story-footer' %}" target="_blank" rel="noopener me">Watch the full story on TikTok →</a></p>
</section>

<footer class="footer">
  <p><a href="{% include utm.html base=site.data.site.tiktok.url slot='footer' %}" target="_blank" rel="noopener me">{{ site.data.site.tiktok.handle }}</a></p>
  <p>© {{ site.time | date: "%Y" }} DBest In Love</p>
  <p>Two flags, one story.</p>
</footer>
