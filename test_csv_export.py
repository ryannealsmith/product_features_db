#!/usr/bin/env python3
"""
Test script to verify CSV export functionality
"""
import requests
import os

def test_csv_export():
    """Test the CSV export endpoint and save to file"""
    url = "http://127.0.0.1:8080/export/miro_csv"
    
    try:
        print("Testing CSV export endpoint...")
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")
        print(f"Content Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            # Save CSV to file
            filename = "exported_miro_data.csv"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"\n✅ CSV export successful!")
            print(f"📁 File saved as: {filename}")
            print(f"📊 File size: {os.path.getsize(filename)} bytes")
            
            # Show first few lines
            lines = response.text.split('\n')
            print(f"\n📋 CSV Preview (first 5 lines):")
            for i, line in enumerate(lines[:5]):
                print(f"  {i+1}: {line}")
            
            print(f"\n📈 Total rows: {len([l for l in lines if l.strip()])}")
            
        else:
            print(f"❌ Export failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on http://127.0.0.1:8080")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_csv_export()