"""
AWS Lambda Handler for UPC Price Lookup

This Lambda function handles UPC price lookups via iHerb API.
It can be invoked via API Gateway or directly.

Event format:
{
    "upcs": ["123456789012", "456789012345"],
    "rate_limit": 20,
    "country_code": "US",
    "currency": "USD"
}

Or for single UPC:
{
    "upc": "123456789012"
}
"""

import json
import time
from typing import Dict, List, Optional
from datetime import datetime
import os

# Import from the main module
try:
    from upc_price_lookup import UPCPriceLookup
except ImportError:
    # If running in Lambda with packaged dependencies
    import sys
    sys.path.insert(0, '/var/task')
    from upc_price_lookup import UPCPriceLookup


def lambda_handler(event, context):
    """
    AWS Lambda handler for UPC price lookups.

    Args:
        event: Lambda event containing UPC codes and configuration
        context: Lambda context

    Returns:
        Response with lookup results
    """
    try:
        # Parse event (handle both API Gateway and direct invocation)
        if isinstance(event.get('body'), str):
            # API Gateway event
            body = json.loads(event['body'])
        else:
            # Direct invocation
            body = event

        # Extract parameters
        upcs = body.get('upcs', [])
        if not upcs and body.get('upc'):
            upcs = [body['upc']]

        rate_limit = int(body.get('rate_limit', os.environ.get('RATE_LIMIT', 20)))
        country_code = body.get('country_code', os.environ.get('COUNTRY_CODE', 'US'))
        currency = body.get('currency', os.environ.get('CURRENCY', 'USD'))

        if not upcs:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'No UPC codes provided',
                    'message': 'Please provide either "upc" or "upcs" in the request body'
                })
            }

        # Check Lambda timeout constraint
        remaining_time = context.get_remaining_time_in_millis() / 1000
        max_upcs = int(remaining_time / (60 / rate_limit)) - 10  # Leave 10s buffer

        if len(upcs) > max_upcs:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Too many UPCs for Lambda timeout',
                    'message': f'Maximum {max_upcs} UPCs can be processed in one invocation',
                    'suggestion': 'Split into multiple requests or increase Lambda timeout'
                })
            }

        # Initialize lookup tool
        lookup = UPCPriceLookup(
            rate_limit=rate_limit,
            country_code=country_code,
            currency=currency
        )

        # Perform lookups (no progress output in Lambda)
        results = lookup.lookup_batch(upcs, progress=False)

        # Calculate statistics
        found = sum(1 for r in results if r.get('found'))
        not_found = len(results) - found

        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'summary': {
                    'total': len(results),
                    'found': found,
                    'not_found': not_found,
                    'success_rate': round(found / len(results) * 100, 1) if results else 0
                },
                'results': results,
                'metadata': {
                    'rate_limit': rate_limit,
                    'country_code': country_code,
                    'currency': currency,
                    'timestamp': datetime.now().isoformat()
                }
            })
        }

    except Exception as e:
        print(f"Error in Lambda handler: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'message': 'Internal server error occurred during UPC lookup'
            })
        }


# For testing locally
if __name__ == "__main__":
    # Test event
    test_event = {
        "upcs": ["NOW-00453", "123456789012"],
        "rate_limit": 20,
        "country_code": "US",
        "currency": "USD"
    }

    # Mock context
    class MockContext:
        def get_remaining_time_in_millis(self):
            return 300000  # 5 minutes

    result = lambda_handler(test_event, MockContext())
    print(json.dumps(json.loads(result['body']), indent=2))
