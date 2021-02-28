# Product Hunt NLP Experiments
Natural Language Processing (NLP) experiments based on data from Product Hunt.

**Development status**: Data collection

## Experiments

- A model that suggests topics based on a description of the product
- A model that comes up describes a product based on given topics
- A model that generates a tagline based on the product description
- A model that creates a name for a product based on its description

## Data collection

If you prefer to skip this step, there is [a relatively old dataset](https://data.world/producthunt) that 
you can use instead.

Product Hunt offers a [free GraphQL API](https://api.producthunt.com/v2/docs) that has a 
[rate limit](https://api.producthunt.com/v2/docs/rate_limits/headers) based on the complexity and frequency of 
the requests.

For more information, please read their [GraphQL reference](http://api-v2-docs.producthunt.com.s3-website-us-east-1.amazonaws.com/operation/query/).
You can use their [GraphQL explorer](https://ph-graph-api-explorer.herokuapp.com/) to practice.

To get started, create a Product Hunt account and proceed with creating a new application in 
the [API dashboard](https://api.producthunt.com/v2/oauth/applications).

We will be using the developer token via [OAuth Client Only Authentication](https://api.producthunt.com/v2/docs/oauth_client_only_authentication/oauth_token_ask_for_client_level_token). 
Copy `config.conf.example` as `config.conf` and insert your developer token.

Run `dataset/populate.py` to start the data collection process. By default, it will  

## About the author

This project was created and is maintained by [Mohammad Tomaraei](https://tomaraei.com).

[![Mohammad Tomaraei](https://raw.githubusercontent.com/themreza/themreza/master/logo-mini.png)](https://tomaraei.com)