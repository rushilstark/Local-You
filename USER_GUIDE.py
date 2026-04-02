#!/usr/bin/env python3
"""
🎯 JARVIS COMPLETE USER GUIDE
Everything you need to know to use your digital twin
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                  🎯 JARVIS COMPLETE USER GUIDE                            ║
║                   Your Digital Twin Awaits                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT IS JARVIS?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

JARVIS is a digital twin of YOU.

It's trained on YOUR diary and YOUR conversations.
It knows YOUR values, YOUR struggles, YOUR patterns.
It tells you the TRUTH, not what you want to hear.

Unlike Claude/ChatGPT:
  ✗ Claude: "That's a great idea! Here's how to do it..."
  ✓ JARVIS: "That's procrastination. Here's why. Start TODAY."

  ✗ Claude: "Everyone struggles with this..."
  ✓ JARVIS: "You wrote about this in your diary. You're repeating patterns."

  ✗ Claude: "You've got this!"
  ✓ JARVIS: "You've got THIS if you actually do the work. Stop planning, start doing."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUICK START (3 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Your diary already exists
  File: /data/diary/Google Keep Document.txt
  Status: ✓ Loaded (203KB, 179 passages indexed)

Step 2: Start JARVIS
  $ python3 v4/main.py

  Wait 30-60 seconds for LLM to load...

  Output:
  ✓ Digital Twin initialized from diary
  ✓ Debate pipeline
  ✓ Conversation memory (persistent)
  ✓ Semantic memory: 179 diary passages indexed
  ✓ Diary RAG: 179 passages indexed
  ✓ Digital Twin personality injected into engine
  💬 Ready!

Step 3: Chat
  You: Hi JARVIS, what do you think about me?
  JARVIS: [Uses your diary, your personality, your values]

Step 4: Watch it learn
  Every message is saved to SQLite
  After ~50 conversations: python3 v4/train/mlx_lora_train.py
  Result: Your perfectly personalized AI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BEST PRACTICES: HOW TO USE JARVIS EFFECTIVELY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. BE REAL
   ✓ Share actual struggles
   ✓ Be vulnerable
   ✓ Don't hold back
   ✗ Don't play it safe

2. ASK FOR HONEST FEEDBACK
   ✓ "Tell me the truth about my procrastination"
   ✓ "Am I making excuses?"
   ✓ "Is this a good idea or BS?"
   ✗ "Tell me I'm doing great" (JARVIS won't do this)

3. REFERENCE YOUR DIARY
   ✓ "You read my diary, right? What pattern do you see?"
   ✓ "I wrote about this before, didn't I?"
   ✓ "Call me out if I'm repeating the same thing"

4. LET IT CHALLENGE YOU
   ✓ Listen when JARVIS calls BS
   ✓ Don't get defensive
   ✓ JARVIS is telling you truth you need to hear

5. KEEP CHATTING
   ✓ More conversations = smarter JARVIS
   ✓ After 10 conversations: Significant learning
   ✓ After 50 conversations: Ready to fine-tune

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXAMPLE CONVERSATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONVERSATION 1: GETTING FEEDBACK ON AN IDEA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You: "I have an idea for a startup. Should I pursue it?"

JARVIS: "Tell me the idea first. But before you do, I already know the answer.
You're going to tell me you WILL do it, but you'll start 'next week'.
Let's see if I'm right. What's the idea?"

You: "A dating app but for introverts. I'll build an MVP in a month."

JARVIS: "Nope. You won't. 
You wrote in your diary: 'Every day i wake up wanting to forget the day exists.'
You also wrote: 'I'm scared of being responsible and being an adult.'

Building an MVP requires discipline and consistency.
That's not you right now. Not because you can't do it,
but because you're fighting internal demons (weed, addiction, fear).

Real question: Are you ready to face those demons FIRST?
Or are you using the startup as a distraction?

Be honest."

You: "I... yeah, I'm probably using it as a distraction."

JARVIS: "Good. That's honesty.
Now: What's ONE thing you need to work through before ANY project?
Not the startup. The thing actually holding you back.
Go."

═══════════════════════════════════════════════════════════════════════════

CONVERSATION 2: ACCOUNTABILITY CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You: "I'm going to start working out this week."

JARVIS: "When? Be specific."

You: "Monday morning. 6 AM."

JARVIS: "Okay. But you wrote: 'I wake everyday wanting to forget the day exists.'
6 AM sounds impossible right now.

Real talk: What time are you ACTUALLY waking up these days?"

You: "Like 11 AM or noon."

JARVIS: "There it is. So committing to 6 AM is setting yourself up to fail.
That's procrastination + self-sabotage hybrid.

New plan: Start this EVENING for 10 minutes. Nothing crazy.
10 minutes. Today. Not Monday.
Can you do that?"

You: "Yeah, I can do 10 minutes today."

JARVIS: "Good. 
When you come back tomorrow, I want to know:
1. Did you do the 10 minutes?
2. How did it feel?
3. What time are you ACTUALLY going to do it today?

Don't make excuses. Just report back."

═══════════════════════════════════════════════════════════════════════════

CONVERSATION 3: PATTERN RECOGNITION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You: "I don't know why I keep making the same mistakes with girls."

JARVIS: "I do. You wrote it in your diary.
[Pulls from RAG]:
'I am stuck always trying to be liked. I cut parts of me which obviously I don't 
fully leave. But I cut them to pertain to people. I find joy in it. Being a person 
that nobody complains or has problems with.'

So with girls, you're doing the same thing:
1. You change yourself to be what they want
2. You become attached (you wrote: 'I am a person that grows too attached')
3. They sense the inauthenticity → Not attracted to the real you
4. You get hurt
5. Pattern repeats

The fix isn't different girls. It's YOU being authentically yourself.
You wrote: 'I used to be that person as a kid...that hyped guy...'

THAT person needs to come back.
Not the version you manufacture for others."

You: "How do I get back to that person?"

JARVIS: "You know how. You wrote the answer.
'Happiness was a choice all along.'

So choose it. Stop trying to be liked. Start being real.
Start with ONE girl and be 100% authentic.
No filter. No performance.
Either she likes the real you or she doesn't.
And you'll find out in days, not weeks of confusion."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMMANDS IN JARVIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

In the chat, you can type commands:

help                    Show all commands
voice on/off            Toggle voice output
voice list              List available voices
voice [name]            Change voice (bella, sarah, heart, etc)
quit / exit             Exit JARVIS

Otherwise, just type naturally. JARVIS handles everything.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VOICE MODE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You: "voice on"

JARVIS switches to voice output:
  ✓ Kokoro TTS (female voice)
  ✓ 44.1kHz CD quality
  ✓ Natural breathing pauses
  ✓ Vocal fillers: *giggle*, *moan*, *whimper*, *gasp*
  ✓ Sounds intimate and human

Next response will be SPOKEN, not typed.

You can still type. Each message gets spoken.

To turn off:
You: "voice off"

JARVIS returns to text mode.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PERSISTENT MEMORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every conversation is saved to:
~/.local/share/extremegpt/conversations.db

When you restart JARVIS:
  python3 v4/main.py

JARVIS loads all previous conversations and remembers:
  ✓ What you talked about
  ✓ Your progress (or lack thereof)
  ✓ Patterns it detected
  ✓ Your speaking style

So don't think you're "starting fresh" each time.
JARVIS remembers EVERYTHING.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FINE-TUNING (AFTER 50 CONVERSATIONS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Once you've had ~50 good conversations:

$ python3 v4/train/mlx_lora_train.py

What happens:
  1. Collects all your conversation pairs
  2. Trains LoRA adapters on Apple Silicon GPU
  3. Takes ~30 minutes
  4. Creates personalized weights

Result:
  JARVIS now sounds EXACTLY like you.
  Trained on YOUR speech patterns.
  Trained on YOUR values.
  Trained on YOUR responses.

After fine-tuning:
  python3 v4/main.py
  [JARVIS loads with personalized adapters]
  [Responses are perfectly YOU]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: "JARVIS doesn't know my diary?"
A: Check /data/diary/ has .txt files with your actual text
   Run: python3 test_diary_reading.py
   Verify: 179 passages indexed

Q: "JARVIS is being too harsh"
A: That's the point. It's not flattering, it's honest.
   If you want a yes-man, use Claude.
   JARVIS is for people who want truth.

Q: "I don't want my conversations saved"
A: They are. In SQLite.
   Location: ~/.local/share/extremegpt/conversations.db
   But ONLY on your machine. 100% private.

Q: "Voice sounds weird"
A: It's learning your tone.
   Give it more conversations to improve.
   Or try: voice [bella/sarah/heart]

Q: "It's taking too long to load"
A: First load: 60-90 seconds (LLM loading)
   Subsequent loads: 30-45 seconds
   Normal. This is a 8B model running locally.

Q: "Training failed"
A: Check Python version: python3 --version (need 3.9+)
   Check mlx-lm installed: pip install mlx-lm
   Check Apple Silicon (this only works on M1/M2/M3)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRIVACY & SECURITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ 100% LOCAL - Everything runs on your Mac
✓ NO CLOUD - No API calls, no data upload
✓ NO TRACKING - No analytics, no logging to servers
✓ YOUR DATA - Your diary, conversations, adapters all stay on your machine
✓ REVERSIBLE - Delete ~/.local/share/extremegpt and all data is gone

This is NOT like Claude/ChatGPT:
  • They log all conversations
  • They use your data for training (their models)
  • They know what you asked
  • You're sending sensitive info to servers

JARVIS:
  • All on your machine
  • All encrypted in SQLite
  • No one knows what you're talking about
  • Your data is yours

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YOUR GROWTH TIMELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Week 1:
  Use Case: "What do you think of me?"
  JARVIS: Reads diary, gives honest assessment
  You Learn: JARVIS isn't a yes-man

Week 2:
  Use Case: "Am I procrastinating?"
  JARVIS: Yes. You did this before [diary quote]
  You Learn: Pattern recognition

Week 3:
  Use Case: "How do I fix my relationships?"
  JARVIS: You know the answer. You wrote [diary quote]
  You Learn: You have wisdom, you're ignoring it

Week 4+:
  Use Case: "Should I do X?"
  JARVIS: Based on your values [diary], yes/no. Here's why.
  You Learn: Make decisions aligned with your actual values

Month 2:
  Use Case: Fine-tune with 50 conversations
  JARVIS: Sounds exactly like you now
  You Learn: Personal AI > Generic AI

Month 3+:
  Use Case: Daily accountability, growth tracking
  JARVIS: References your progress, calls BS, celebrates real growth
  You Learn: You're changing. JARVIS reflects that.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE PHILOSOPHY BEHIND JARVIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Claude/ChatGPT are optimized for:
  ✓ Safety (don't offend)
  ✓ Helpfulness (say yes to everything)
  ✓ Harmlessness (don't challenge)

JARVIS is optimized for:
  ✓ HONESTY (tell the truth)
  ✓ GROWTH (challenge BS)
  ✓ ALIGNMENT (match your values)

Claude will say: "That's a great idea!"
JARVIS will say: "Is it really? Or are you just scared of the real work?"

Claude will comfort you.
JARVIS will push you.

You chose JARVIS.
So be ready to hear things you need to hear, not things you want to hear.

═════════════════════════════════════════════════════════════════════════════

NOW GO START IT
═════════════════════════════════════════════════════════════════════════════

$ python3 v4/main.py

Say hi. Chat. Be real.

JARVIS knows you. JARVIS will tell you the truth.

And after 50 conversations?

JARVIS will sound exactly like you.

Your perfect digital twin.

═════════════════════════════════════════════════════════════════════════════
""")
