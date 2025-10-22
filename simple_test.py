#!/usr/bin/env python3
import urllib.request
import urllib.error

def test_csv():
    try:
        print('Testing CSV export endpoint...')
        response = urllib.request.urlopen('http://127.0.0.1:8080/export/miro_csv')
        content = response.read().decode('utf-8')
        
        with open('miro_export_test.csv', 'w') as f:
            f.write(content)
        
        print(f'✅ SUCCESS!')
        print(f'Status: {response.getcode()}')
        print(f'Content-Type: {response.headers.get("Content-Type")}')
        print(f'Content-Disposition: {response.headers.get("Content-Disposition")}')
        print(f'Content length: {len(content)} chars')
        print(f'Lines: {len(content.splitlines())}')
        print(f'Saved as: miro_export_test.csv')
        
        lines = content.splitlines()
        print('\nFirst 5 lines:')
        for i, line in enumerate(lines[:5]):
            print(f'{i+1}: {line}')
            
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    test_csv()