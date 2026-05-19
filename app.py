def filtered_rank_tool():
    entries = []
    MAX_RANK = 30000
    
    print(f"--- Rank Organizer (Filtered for < {MAX_RANK}) ---")
    print("Type 'done' to finish.\n")
    
    while True:
        college = input("College: ")
        if college.lower() == 'done': break
        
        branch = input("Branch: ")
        try:
            rank = float(input("Rank: "))
            # Only add if it's within your 30k limit
            if rank <= MAX_RANK:
                entries.append({"cllg": college, "br": branch, "rank": rank})
            else:
                print(f"⏩ Skipping {college} {branch} (Rank {rank} is > 30,000)")
        except ValueError:
            print("Invalid input.")
        print("-" * 20)

    # Sorting
    sorted_data = sorted(entries, key=lambda x: x['rank'])

    print(f"\n--- Sorted Results (Under {MAX_RANK}) ---")
    for i, item in enumerate(sorted_data, 1):
        print(f"{i}. {item['rank']} | {item['cllg']} | {item['br']}")

if __name__ == "__main__":
    filtered_rank_tool()
