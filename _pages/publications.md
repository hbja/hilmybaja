---
layout: default
title: "Publications"
permalink: /publications/
publications:
- title: "APPLE MOTS: Detection, Segmentation and Tracking of Homogeneous Objects Using MOTS"
  authors: "S de Jong, H Baja, K Tamminga, J Valente"
  journal: "IEEE Robotics and Automation Letters"
  year: 2022
  doi: "10.1109/LRA.2022.3199026"
  link: "https://ieeexplore.ieee.org/document/9857971"

- title: "Object detection and tracking on UAV RGB videos for early extraction of grape phenotypic traits"
  authors: "M Ariza-Sentís, H Baja, S Vélez, J Valente"
  journal: "Computers and Electronics in Agriculture"
  year: 2023
  doi: "10.1016/j.compag.2023.108051"
  link: "https://www.sciencedirect.com/science/article/pii/S0168169923004398"

- title: "An aerial framework for Multi-View grape bunch detection and route Optimization using ACO"
  authors: "M Ariza-Sentís, S Vélez, H Baja, R Valenti, J Valente"
  journal: "Computers and Electronics in Agriculture"
  year: 2023
  doi: "10.1016/j.compag.2024.108972"
  link: "https://www.sciencedirect.com/science/article/pii/S0168169924003636"

- title: "Object Detection and Tracking in Precision Farming: A Systematic Review"
  authors: "M Ariza-Sentís, S Vélez, R Martínez-Peña, H Baja, J Valente"
  journal: "Computers and Electronics in Agriculture"
  year: 2024
  doi: "doi.org/10.1016/j.compag.2024.108757"
  link: "https://www.sciencedirect.com/science/article/pii/S0168169924001480"

- title: "Comparative analysis of single-view and multiple-view data collection strategies for detecting partially-occluded grape bunches: Field trials"
  authors: "M Ariza-Sentís, H Baja, S Vélez, Rick van Essen, J Valente"
  journal: "Journal of Agriculture and Food Research"
  year: 2025
  doi: "10.1016/j.jafr.2025.101736"
  link: "https://www.sciencedirect.com/science/article/pii/S2666154325001073"

- title: "To Measure or Not: A Cost-Sensitive, Selective Measuring Environment for Agricultural Management Decisions with Reinforcement Learning"
  authors: "H Baja, M Kallenberg, I Athanasiadis"
  journal: "AAAI Conference on Artificial Intelligence"
  year: 2025
  doi: "doi.org/10.48550/arXiv.2501.12823"
  link: "https://arxiv.org/abs/2501.12823"
---

<h2>My Scientific Publications</h2>

{% assign sorted_pubs = page.publications | sort: "year" | reverse %}

{% for pub in sorted_pubs %}
  <div class="publication-entry">
    <h3><a href="{{ pub.link }}" target="_blank">{{ pub.title }}</a></h3>
    <p><strong>Authors</strong>: {% assign formatted_authors = pub.authors | replace: "H Baja", "<strong>H Baja</strong>" %}
        {{ formatted_authors }}</p>
    <p><strong>Journal:</strong> {{ pub.journal }}</p>
    <p><strong>Year:</strong> {{ pub.year }}</p>

    {% if pub.doi %}
      <p><strong>DOI:</strong> <a href="https://doi.org/{{ pub.doi }}" target="_blank">{{ pub.doi }}</a></p>
    {% endif %}
  </div>
{% endfor %}