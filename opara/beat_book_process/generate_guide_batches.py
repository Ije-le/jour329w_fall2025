import subprocess
import time

# Read the prompt and combined file
with open('guideprompt.txt', 'r') as f:
    prompt = f.read()

with open('combined.txt', 'r') as f:
    content = f.read()

# Split content into chunks (approximately 2500 lines or 200KB per chunk to be safe)
lines = content.split('\n')
chunk_size = 2500
chunks = []

for i in range(0, len(lines), chunk_size):
    chunk = '\n'.join(lines[i:i + chunk_size])
    chunks.append(chunk)

print(f"Split into {len(chunks)} chunks")

# Process each chunk
results = []
for i, chunk in enumerate(chunks):
    print(f"\nProcessing chunk {i+1}/{len(chunks)}...")
    
    # Create a modified prompt for continuation chunks
    if i == 0:
        batch_prompt = prompt
    else:
        batch_prompt = f"""Continue building the beat book guide. This is part {i+1} of {len(chunks)}.
        
Previous parts have covered earlier material. Continue adding to the guide based on this additional content.
Do not repeat the introduction or earlier sections.

{prompt}"""
    
    # Combine prompt and chunk
    input_text = f"{batch_prompt}\n\n{chunk}"
    
    # Send to LLM
    try:
        result = subprocess.run(
            ['uv', 'run', 'llm', '-m', 'groq/openai/gpt-oss-120b'],
            input=input_text,
            text=True,
            capture_output=True,
            timeout=120
        )
        
        if result.returncode == 0:
            results.append(result.stdout)
            print(f"✓ Chunk {i+1} processed successfully ({len(result.stdout)} chars)")
        else:
            print(f"✗ Error processing chunk {i+1}: {result.stderr}")
            results.append(f"\n\n--- ERROR IN CHUNK {i+1} ---\n{result.stderr}\n")
    
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout processing chunk {i+1}")
        results.append(f"\n\n--- TIMEOUT IN CHUNK {i+1} ---\n")
    
    except Exception as e:
        print(f"✗ Exception processing chunk {i+1}: {e}")
        results.append(f"\n\n--- EXCEPTION IN CHUNK {i+1}: {e} ---\n")
    
    # Small delay between requests
    if i < len(chunks) - 1:
        time.sleep(2)

# Combine all results
print("\nCombining results...")
combined_output = '\n\n---\n\n'.join(results)

with open('guide_notes.md', 'w') as f:
    f.write(combined_output)

print(f"\n✓ Complete! Generated guide_notes.md with {len(results)} sections")
print(f"Total output length: {len(combined_output)} characters")
