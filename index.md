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
       href="{{ link.url }}"
       {% if link.external %}target="_blank" rel="noopener"{% endif %}>
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

  {%- assign published = site.episodes | where: "draft", false -%}
  {%- if published.size == 0 -%}
  {%- comment -%}
    Stage 2 degradation path (REDESIGN_PLAN): zero published episodes -> the
    prose story renders from _data/chapters.yml blurbs. Same words as before,
    now owned by data instead of HTML. When episode #1 is un-drafted, Stage 4's
    full chronology loop replaces this block.
  {%- endcomment -%}
  {%- for ch in site.data.chapters %}
  <p>{{ ch.blurb }}</p>
  {%- endfor -%}
  {%- else -%}
  {%- comment %}Stage 4 renders the full chapter × episode chronology here.
  The featured pin below already works from Stage 2 data.{% endcomment -%}
  {%- assign feat = published | where: "featured", true | first -%}
  {%- if feat %}
  <p><a class="text-link" href="{{ feat.url | relative_url }}">Begin with Episode {{ feat.episode }}: {{ feat.title }} →</a></p>
  {%- endif -%}
  {%- endif -%}

  <p><a class="text-link" href="{{ site.data.site.tiktok.url }}" target="_blank" rel="noopener">Watch the full story on TikTok →</a></p>
</section>

<footer class="footer">
  <p><a href="{{ site.data.site.tiktok.url }}" target="_blank" rel="noopener">{{ site.data.site.tiktok.handle }}</a></p>
  <p>© {{ site.time | date: "%Y" }} DBest In Love</p>
  <p>Two flags, one story.</p>
</footer>
