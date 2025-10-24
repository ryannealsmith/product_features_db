#!/usr/bin/env python3
from app import app, db, Capabilities, TechnicalFunction

def check_long_names():
    with app.app_context():
        caps = Capabilities.query.all()
        
        print("Checking for capabilities with long names...")
        long_names = [cap for cap in caps if len(cap.name) > 50]
        for cap in long_names[:5]:
            print(f"  {len(cap.name)} chars: \"{cap.name[:80]}...\"")
        
        print(f"\nFound {len(long_names)} capabilities with names longer than 50 characters")
        
        # Check technical functions too
        tech_funcs = TechnicalFunction.query.all()
        long_tf_names = [tf for tf in tech_funcs if len(tf.name) > 50]
        for tf in long_tf_names[:5]:
            print(f"  TF {len(tf.name)} chars: \"{tf.name[:80]}...\"")
        
        print(f"\nFound {len(long_tf_names)} technical functions with names longer than 50 characters")

if __name__ == "__main__":
    check_long_names()