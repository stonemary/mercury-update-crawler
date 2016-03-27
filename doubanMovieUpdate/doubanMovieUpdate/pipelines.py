# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from __future__ import print_function
import json
import decimal
from logging import getLogger

import boto3


log = getLogger(__name__)


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


class DoubanmovieupdatePipeline(object):

    def __init__(self):
        self.table_name = 'Movies'
        self.dynamodb = boto3.resource('dynamodb',region_name='us-west-2', endpoint_url="https://dynamodb.us-west-2.amazonaws.com")

    def process_item(self, item, spider):

        log.info('updating table: ' + self.table_name)

        table = self.dynamodb.Table(self.table_name)

        movie = dict(item)
        name = movie['name'][0]
        movie_id = movie['movieid']
        year = movie['year'][0] if movie['year'] else '0000'
        score = movie['score'][0] if movie['score'] else '0.01'
        classification = movie['classification']
        poster_url = movie['poster_url']
        actor = movie['actor']
        director = movie['director']
                        
        log.info('Adding movie ' + name)
                        
        response = table.put_item(
            Item={
                'name': name,
                'movie_id': movie_id,
                'year': year,
                'score': score,
                'classification': classification,
                'poster_url': poster_url,
                'actor': actor,
                'director': director
            }
        )
                                                  
        log.debug("PutItem succeeded: \n{}".format(json.dumps(response, indent=4, cls=DecimalEncoder)))
        return item

