---
layout: page
title: "Publications"
permalink: /publications/
---

{% assign publications = site.data.publications.items | sort: "year" | reverse %}

<section class="publications-intro">
  <p>
    A continuously updated list of my publications, with quick badges for venue, topic, citations, DOI, and related material.
    You can also browse the source profile on <a href="{{ site.scholar.profile_url }}" target="_blank" rel="noopener noreferrer">Google Scholar</a>.
  </p>
  {% if site.data.publications.generated_at %}
    <p class="publications-sync-note">Last synced: {{ site.data.publications.generated_at | date: "%d %b %Y" }}</p>
  {% endif %}
</section>

<section class="publications-list">
  {% for pub in publications %}
    {% include publication_card.html publication=pub %}
  {% endfor %}
</section>
