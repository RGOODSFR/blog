Title: PyConFR 2024 : On a créé notre SaaS avec Wagtail
Date: 2024-11-03 08:00
Id: 0005
Slug: pyconfr24-on-a-cree-notre-saas-avec-wagtail
Lang: fr
Category: communauté
Tags: django, wagtail
Summary: Un résumé de notre présentation lors de la PyConFR 2024 à Strasbourg le 03/11/2024

# PyConFR 2024

Lors de la [PyConFR 2024](https://www.pycon.fr/2024/) qui se tenait à Strasbourg de 31 octobre au 3 novembre 2024, nous avons fait une présentation : "*Retour d'expérience : on a créé notre SaaS avec le CMS Wagtail*".

Les objectifs de cette présentation étaient de:
1. présenter le CMS Wagtail et comment nous nous sommes appropriés l'utilisation de ses fonctionnalités natives ([Streamfields](https://docs.wagtail.org/en/v2.16.1/topics/streamfield.html), [Live preview](https://docs.wagtail.org/en/v4.0.3/editor_manual/new_pages/previewing_and_submitting_for_moderation.html), etc.)
1. montré comment nous avons créé de nouvelles fonctionnalités afin de créer un produit sur mesure (gestion des traductions, controlleurs [Stimulus](https://docs.wagtail.org/en/stable/contributing/ui_guidelines.html#stimulus), feature [Draftail](https://www.draftail.org/), etc.)
1. donner quelques conseils sur l'utilisation du CMS

Les slides de la présentation sont disponibles ici :
[PyconFR 2024 : On a créé notre SaaS avec Wagtail]({attach}/downloads/pyconfr24-on-a-cree-notre-saas-avec-wagtail.pdf)

## Nous avons aussi retenu

- [Une application versionnée automatiquement](https://www.pycon.fr/2024/fr/talks/short-talk.html#talk-9YNYJQ)
  - Utilisation du package `python-semantic-version`
  - Se base sur les noms des commits ([convention de nommage Angular](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits)) afin de créer des sous-versions automatiquement
  - [Billet de blog](https://rigaudie.fr/article/python/generer-une-application-versionnee-automatiquement-avec-une-release-semantique/)


- [Mettre à jour le schéma d'une vaste base de données sans downtime et sans stress](https://www.pycon.fr/2024/fr/talks/short-talk.html#talk-WQEXVB)
  - L'équipe du Pass Culture a présenté sa manière de faire du "zero-downtime deployment"
  - Gestion des migrations avec [Flask + SQLAlchemy](https://flask-sqlalchemy.readthedocs.io/en/stable/)
  - Système de branches de migration (Alembic) pre/post

- [Tempête de boulettes géantes](https://www.pycon.fr/2024/fr/talks/long-talk.html#talk-7DNDLP)
  - Un retour d'expérience de la communauté sur les "boulettes", ces erreurs que l'ont fait en production et qui peuvent avoir de grandes conséquences
  - Un classement de celles-ci par typologie et les solutions à mettre en place pour ne pas les reproduire ou les éviter
