import streamlit as st


class HealthAwarenessApp:

    def __init__(self):

        self.health_topics = [
            "Healthy Diet",
            "Exercise & Fitness",
            "Mental Health",
            "Disease Prevention",
            "Personal Hygiene",
            "Water & Hydration",
            "Emergency Information"
        ]

        self.information = {
            "Healthy Diet":
                "Eat fruits, vegetables, whole grains and "
                "other nutritious foods.",

            "Exercise & Fitness":
                "Regular physical activity helps maintain "
                "overall fitness and well-being.",

            "Mental Health":
                "Take adequate rest, stay connected with "
                "others and seek professional help when needed.",

            "Disease Prevention":
                "Maintain hygiene, follow recommended "
                "preventive measures and get appropriate checkups.",

            "Personal Hygiene":
                "Wash your hands regularly and maintain "
                "good personal cleanliness.",

            "Water & Hydration":
                "Drink adequate fluids according to your "
                "individual needs and circumstances.",

            "Emergency Information":
                "In an emergency, contact your local "
                "emergency medical service."
        }

    def build(self):

        st.title("HEALTH AWARENESS CAMPAIGN")

        for topic in self.health_topics:

            if st.button(topic, use_container_width=True):

                st.session_state["topic"] = topic

                st.rerun()

    def show_information(self, topic):

        st.title(topic)

        st.write(
            self.information.get(topic, "")
        )

        if st.button("← Back", use_container_width=True):

            st.session_state["topic"] = None

            st.rerun()

    def run(self):

        if "topic" not in st.session_state:

            st.session_state["topic"] = None

        if st.session_state["topic"] is None:

            self.build()

        else:

            self.show_information(
                st.session_state["topic"]
            )


if __name__ == "__main__":

    st.set_page_config(
        page_title="Health Awareness Campaign"
    )

    app = HealthAwarenessApp()

    app.run()
