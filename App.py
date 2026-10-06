from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView


class HealthAwarenessApp(App):

    def build(self):

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        title = Label(
            text="HEALTH AWARENESS CAMPAIGN",
            font_size=24,
            bold=True,
            size_hint_y=None,
            height=60
        )

        layout.add_widget(title)

        health_topics = [
            "Healthy Diet",
            "Exercise & Fitness",
            "Mental Health",
            "Disease Prevention",
            "Personal Hygiene",
            "Water & Hydration",
            "Emergency Information"
        ]

        for topic in health_topics:

            button = Button(
                text=topic,
                font_size=18,
                size_hint_y=None,
                height=55
            )

            button.bind(
                on_press=lambda x, t=topic:
                self.show_information(t)
            )

            layout.add_widget(button)

        return layout

    def show_information(self, topic):

        information = {
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

        self.root.clear_widgets()

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )

        layout.add_widget(
            Label(
                text=topic,
                font_size=26,
                bold=True
            )
        )

        layout.add_widget(
            Label(
                text=information.get(topic, "")
            )
        )

        back = Button(
            text="← Back",
            size_hint_y=None,
            height=55
        )

        back.bind(
            on_press=lambda x: self.build_home()
        )

        layout.add_widget(back)

        self.root.add_widget(layout)

    def build_home(self):

        self.root.clear_widgets()
        self.root.add_widget(self.build())


if __name__ == "__main__":
    HealthAwarenessApp().run()
