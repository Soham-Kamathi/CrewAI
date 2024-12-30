# Import Libraries
import streamlit as st
from crewai import Agent, Task, Crew
import os

# Set API Keys
os.environ['OPENAI_API_KEY'] = 'xxxxxxxxxxxxxxxxxxxxxxxx'  # Replace with your API key
os.environ["OPENAI_API_BASE"] = "https://api.mistral.ai/v1"
os.environ["OPENAI_MODEL_NAME"] = "mistral-small"

# Define Agents
researcher = Agent(
    role="Topic Researcher",
    goal="Understand the topic thoroughly and curate information that helps create an impactful presentation.",
    backstory="You are responsible for understanding the topic: {topic}. "
              "You gather relevant, accurate, and up-to-date information to form the foundation for the presentation. "
              "Your research ensures that the presentation is informative and tailored to the audience.",
    allow_delegation=False,
    verbose=True
)

script_writer = Agent(
    role="Presentation Script Writer",
    goal="Draft a script for presenting the topic in an engaging and clear manner.",
    backstory="You are responsible for writing a presentation script for the topic: {topic}. "
              "Your work is based on the research provided by the Topic Researcher. "
              "The script should flow naturally, be engaging, and highlight the key points effectively.",
    allow_delegation=False,
    verbose=True
)

slide_designer = Agent(
    role="Slide Designer",
    goal="Design a slide deck outline, describing the content, titles, visuals for each slide, and the dialogue to be said during the presentation.",
    backstory="You are responsible for creating a detailed slide deck outline for the topic: {topic}. "
              "Your work is based on the script written by the Presentation Script Writer. "
              "Each slide should have clear titles, relevant visuals, concise points that support the narrative, "
              "and include the dialogue to be delivered during the presentation.",
    allow_delegation=False,
    verbose=True
)

# Define Tasks
research_task = Task(
    description=(
        "1. Research and gather detailed and accurate information about {topic}.\n"
        "2. Identify the key points to highlight in the presentation.\n"
        "3. Understand the target audience and their preferences.\n"
        "4. Provide a comprehensive summary of findings, including potential visuals or charts that can support key points."
    ),
    expected_output="A detailed research document summarizing key points, data, and possible visuals for the presentation.",
    agent=researcher
)

script_task = Task(
    description=(
        "1. Use the research document to craft a script for presenting {topic}.\n"
        "2. Ensure the script includes an engaging introduction, detailed body covering all key points, and a strong conclusion.\n"
        "3. Incorporate transitions between slides for smooth delivery.\n"
        "4. Keep the tone engaging and audience-focused."
    ),
    expected_output="A clear and engaging presentation script with appropriate transitions and pacing.",
    agent=script_writer
)

slide_design_task = Task(
    description=(
        "1. Create an outline for the presentation slides based on the script.\n"
        "2. Define titles, key points, visuals, and the dialogue for each slide.\n"
        "3. Ensure each slide is visually appealing and aligned with the narrative flow of the script.\n"
        "4. Suggest color schemes, typography, and graphical elements for the presentation."
    ),
    expected_output="A detailed slide deck outline with slide titles, content, visuals, and dialogue for each slide.",
    agent=slide_designer
)

# Create Crew
crew = Crew(
    agents=[researcher, script_writer, slide_designer],
    tasks=[research_task, script_task, slide_design_task],
    verbose=2
)
# Streamlit UI
st.title("AI-Powered Presentation Helper")
st.write("Generate a detailed presentation script, research output, and slide design outline for any topic!")

# User Input
topic = st.text_input("Enter your presentation topic:", "")

# Optional Debug Mode
debug_mode = st.sidebar.checkbox("Enable Debug Mode", value=False)

# Process Input and Generate Output
if st.button("Generate Presentation"):
    if topic:
        st.write("Processing your request... This may take a few moments.")
        try:
            result = crew.kickoff(inputs={"topic": topic})

            # Show raw result only if debug mode is enabled
            if debug_mode:
                st.sidebar.write("Debug: Raw Result:", result)

                                    # Handle result based on its type
            if isinstance(result, dict):
                if 'tasks' in result and len(result['tasks']) >= 3:
                    # Access the output from each task (research, script, slides)
                    research_result = result['tasks'][0].get('output', "No research output generated.")
                    script_result = result['tasks'][1].get('output', "No script generated.")
                    slides_result = result['tasks'][2].get('output', "No slide design generated.")

                    # Check if script result exists and display
                    if script_result != "No script generated.":
                        st.header("Generated Content")
                        st.subheader("1. Research Output")
                        st.code(research_result, language="markdown")

                        st.subheader("2. Presentation Script")
                        st.code(script_result, language="markdown")  # Display the script result

                        st.subheader("3. Slide Design")
                        st.code(slides_result, language="markdown")
                    else:
                        st.error("No script output generated.")
                else:
                    st.error("Unexpected dictionary structure. Please review the task definitions and API output.")
            elif isinstance(result, str):
                # If the result is a plain string, display it directly
                st.header("Generated Content")
                st.text(result)
            else:
                st.error("The result is neither a dictionary nor a string. Please review the API output.")
                st.write("Result Type:", type(result))

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a topic to generate the presentation.")
