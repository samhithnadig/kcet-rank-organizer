def rank_organizer_with_branches():
    entries = []
    
    print("--- KEA Engineering Rank Organizer ---")
    print("Enter 'done' in the college name to finish entering data.\n")
    
    while True:
        college = input("Enter College Name/Code: ")
        if college.lower() == 'done':
            break
            
        branch = input(f"Enter Branch Name for {college}: ")
        
        try:
            rank = float(input(f"Enter GM Cut-off Rank for {branch}: "))
            entries.append({
                "college": college, 
                "branch": branch, 
                "rank": rank
            })
        except ValueError:
            print("❌ Invalid rank. Please enter a numerical value.")
            continue
        print("-" * 30)

    # Sort by rank (Ascending order)
    sorted_entries = sorted(entries, key=lambda x: x['rank'])

    # Display results
    print("\n" + "="*60)
    print(f"{'Order':<5} | {'Rank':<10} | {'College':<20} | {'Branch'}")
    print("-" * 60)
    
    for i, entry in enumerate(sorted_entries, 1):
        print(f"{i:<5} | {entry['rank']:<10} | {entry['college']:<20} | {entry['branch']}")
    print("="*60)

if __name__ == "__main__":
    rank_organizer_with_branches()
