import streamlit as st

def get_grade_point(score):
    if score >= 70:
        return 5
    elif score >= 60:
        return 4
    elif score >= 50:
        return 3
    elif score >= 45:
        return 2
    elif score >= 40:
        return 1
    else:
        return 0


def get_grade(score):
    if score >= 70:
        return "A"
    elif score >= 60:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 45:
        return "D"
    elif score >= 40:
        return "E"
    else:
        return "F"


st.title("🎓 CGPA Calculator")

num_courses = st.number_input(
    "Enter number of courses",
    min_value=1,
    step=1
)

total_weighted_points = 0
total_units = 0

for i in range(int(num_courses)):
    st.subheader(f"Course {i + 1}")

    score = st.number_input(
        f"Score for Course {i + 1}",
        min_value=0,
        max_value=100,
        key=f"score_{i}"
    )

    unit = st.number_input(
        f"Unit for Course {i + 1}",
        min_value=1,
        key=f"unit_{i}"
    )

    grade = get_grade(score)
    grade_point = get_grade_point(score)

    st.write(f"**Grade:** {grade}")
    st.write(f"**Grade Point:** {grade_point}")

    total_weighted_points += grade_point * unit
    total_units += unit


if st.button("Calculate CGPA"):
    cgpa = total_weighted_points / total_units
    st.success(f"Your CGPA is: **{cgpa:.2f}**")
