#!/usr/bin/env python
"""
Generate sample CSV files for testing the product importer.
"""

import csv
import argparse
import random


def generate_sample_csv(filename, num_records=1000):
    """
    Generate a sample CSV file with product data.
    
    Args:
        filename: Output CSV filename
        num_records: Number of product records to generate
    """
    print(f"Generating {num_records} sample products...")
    
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Toys']
    adjectives = ['Premium', 'Deluxe', 'Professional', 'Standard', 'Basic', 'Advanced']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['sku', 'name', 'description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for i in range(1, num_records + 1):
            category = random.choice(categories)
            adjective = random.choice(adjectives)
            
            sku = f'SKU{i:06d}'
            name = f'{adjective} {category} Product {i}'
            description = f'This is a high-quality {adjective.lower()} product in the {category} category. ' \
                         f'Perfect for all your needs. Item number {i}.'
            
            writer.writerow({
                'sku': sku,
                'name': name,
                'description': description
            })
            
            if i % 10000 == 0:
                print(f"  Generated {i} records...")
    
    print(f"✅ Successfully generated {filename} with {num_records} records!")


def main():
    parser = argparse.ArgumentParser(
        description='Generate sample CSV files for product import testing'
    )
    parser.add_argument(
        '-o', '--output',
        default='sample_products.csv',
        help='Output CSV filename (default: sample_products.csv)'
    )
    parser.add_argument(
        '-n', '--num-records',
        type=int,
        default=1000,
        help='Number of product records to generate (default: 1000)'
    )
    
    args = parser.parse_args()
    
    generate_sample_csv(args.output, args.num_records)


if __name__ == '__main__':
    main()

