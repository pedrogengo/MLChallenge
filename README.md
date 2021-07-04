# MLChallenge

<p align="center"><img width=12.5% src="https://upload.wikimedia.org/wikipedia/en/thumb/2/20/MercadoLibre.svg/1200px-MercadoLibre.svg.png"></p>

## Overview

In this challenge we developed a crawler application which retrieve information about how many times a link was referenced in another page and save this information in a database. After that, we enriched each link with features of themself. With this features, we made a model to predict references of a link and serves this model in a REST API.

## Goals

1. Develop a Crawler that saves link references in a database;
2. Develop an API do get features of links (if the link already exists use it features, else create then);
3. Train a Random Forest that predict link references;
4. Deploy this model and serves with an API.

## Architecture

## Understanding the repository

