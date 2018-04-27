from big_ol_pile_of_manim_imports import *

X_COLOR = GREEN
Y_COLOR = RED
Z_COLOR = BLUE
OUTPUT_COLOR = YELLOW
INPUT_COLOR = MAROON_B


def get_cramer_matrix(matrix, output_vect, index=0):
    """
    The inputs matrix and output_vect should be Matrix mobjects
    """
    new_matrix = np.array(matrix.mob_matrix)
    new_matrix[:, index] = output_vect.mob_matrix[:, 0]
    # Create a new Matrix mobject with copies of these entries
    result = Matrix(new_matrix, element_to_mobject=lambda m: m.copy())
    result.match_height(matrix)
    return result


class LinearSystem(VGroup):
    CONFIG = {
        "matrix_config": {
            "element_to_mobject": Integer,
        },
        "dimensions": 3,
        "min_int": -9,
        "max_int": 10,
        "height": 4,
    }

    def __init__(self, matrix=None, output_vect=None, **kwargs):
        VGroup.__init__(self, **kwargs)
        if matrix is None:
            dim = self.dimensions
            matrix = np.random.randint(
                self.min_int,
                self.max_int,
                size=(dim, dim)
            )
        else:
            dim = len(matrix)
        self.matrix_mobject = Matrix(matrix, **self.matrix_config)
        self.equals = TexMobject("=")
        self.equals.scale(1.5)

        colors = [X_COLOR, Y_COLOR, Z_COLOR][:dim]
        chars = ["x", "y", "z"][:dim]
        self.input_vect_mob = Matrix(np.array(chars))
        self.input_vect_mob.elements.set_color_by_gradient(*colors)

        if output_vect is None:
            output_vect = np.random.randint(self.min_int, self.max_int, size=(dim, 1))
        self.output_vect_mob = IntegerMatrix(output_vect)
        self.output_vect_mob.elements.set_color(OUTPUT_COLOR)

        for mob in self.matrix_mobject, self.input_vect_mob, self.output_vect_mob:
            mob.scale_to_fit_height(self.height)

        self.add(
            self.matrix_mobject,
            self.input_vect_mob,
            self.equals,
            self.output_vect_mob,
        )
        self.arrange_submobjects(RIGHT, buff=SMALL_BUFF)


# Scenes


class LeaveItToComputers(TeacherStudentsScene):
    CONFIG = {
        "random_seed": 1,
    }

    def construct(self):
        system = LinearSystem(height=3)
        system.next_to(self.pi_creatures, UP)
        system.generate_target()
        system.target.scale(0.5)
        system.target.to_corner(UL)

        cramer_groups = VGroup()
        for i in range(3):
            numer_matrix = get_cramer_matrix(
                system.matrix_mobject, system.output_vect_mob,
                index=i
            )
            numer = VGroup(
                get_det_text(numer_matrix, initial_scale_factor=4),
                numer_matrix
            )
            numer.to_corner(UP)
            denom_matrix_mobject = system.matrix_mobject.copy()
            denom = VGroup(
                get_det_text(denom_matrix_mobject, initial_scale_factor=4),
                denom_matrix_mobject,
            )
            rhs = VGroup(numer, Line(LEFT, RIGHT).match_width(numer), denom)
            rhs.arrange_submobjects(DOWN)
            rhs.scale_to_fit_height(2.25)
            rhs.move_to(self.hold_up_spot, DOWN)
            equals = TexMobject("=").next_to(rhs, LEFT)
            variable = system.input_vect_mob.elements[i].copy()
            variable.next_to(equals, LEFT)
            cramer_group = VGroup(variable, equals, rhs)
            cramer_group.variable = variable
            cramer_group.equals = equals
            cramer_group.rhs = rhs
            cramer_groups.add(cramer_group)

        self.play(
            Write(system),
            self.teacher.change, "raise_right_hand",
            self.get_student_changes("pondering", "thinking", "hooray")
        )
        self.wait(2)
        self.play(
            PiCreatureSays(
                self.teacher, "Let the computer \\\\ handle it",
                target_mode="shruggie",
            ),
            MoveToTarget(system, path_arc=90 * DEGREES),
            self.get_student_changes(*["confused"] * 3)
        )
        self.wait(3)

        cg = cramer_groups[0]
        scale_factor = 1.5
        cg.scale(scale_factor, about_edge=DOWN)
        numer, line, denom = cg.rhs
        x_copy = system.input_vect_mob.elements[0].copy()
        self.play(
            RemovePiCreatureBubble(self.teacher, target_mode="raise_right_hand"),
            ShowCreation(line),
            ReplacementTransform(
                system.matrix_mobject.copy(),
                denom[1],
            ),
            Write(denom[0]),
            FadeIn(cg.equals),
            ReplacementTransform(x_copy, cg.variable),
        )
        denom_mover = denom.deepcopy()
        denom_mover.target = numer.deepcopy()
        column1 = VGroup(*denom_mover.target[1].mob_matrix[:, 0])
        column1.set_fill(opacity=0)
        self.play(MoveToTarget(denom_mover))
        self.look_at(system)
        self.play(
            ReplacementTransform(
                system.output_vect_mob.elements.copy(),
                VGroup(*numer[1].mob_matrix[:, 0]),
                path_arc=180 * DEGREES
            ),
            self.teacher.change, "happy",
        )
        self.remove(denom_mover)
        self.add(cg)
        self.change_all_student_modes("sassy")
        self.wait(2)
        self.play(
            cramer_groups[0].scale, 1 / scale_factor,
            cramer_groups[0].next_to, cramer_groups[1], LEFT, MED_LARGE_BUFF,
            FadeIn(cramer_groups[1]),
            FadeOut(system),
            self.get_student_changes(*3 * ["horrified"], look_at_arg=UP),
        )
        self.wait()
        self.play(
            FadeIn(cramer_groups[2]),
            cramer_groups[:2].next_to, cramer_groups[2], LEFT, MED_LARGE_BUFF,
            self.get_student_changes(*3 * ["horrified"], look_at_arg=UP),
        )
        self.wait()

        brace = Brace(cramer_groups, UP)
        rule_text = brace.get_text("``Cramer's rule''")

        self.play(
            GrowFromCenter(brace),
            Write(rule_text),
            self.get_student_changes(
                "pondering", "erm", "maybe",
                look_at_arg=brace,
            )
        )
        self.wait(3)


class PrerequisiteKnowledge(TeacherStudentsScene):
    CONFIG = {
        "camera_config": {"background_alpha": 255}
    }

    def construct(self):
        self.remove(*self.pi_creatures)
        randy = self.students[1]
        self.add(randy)

        title = TextMobject("Prerequisites")
        title.to_edge(UP)

        h_line = Line(LEFT, RIGHT).scale(5)
        h_line.next_to(title, DOWN)

        images = Group(*[
            ImageMobject("eola%d_thumbnail" % d)
            for d in [5, 6, 7]
        ])
        images.arrange_submobjects(RIGHT, buff=LARGE_BUFF)
        images.next_to(h_line, DOWN, MED_LARGE_BUFF)
        for image in images:
            rect = SurroundingRectangle(image, color=BLUE)
            image.rect = rect

        self.add(title)
        self.play(
            ShowCreation(h_line),
            randy.change, "erm"
        )
        self.wait()
        for image in images:
            self.play(
                FadeInFromDown(image),
                FadeInFromDown(image.rect),
                randy.change, "pondering"
            )
            self.wait()


class NotTheMostComputationallyEfficient(Scene):
    CONFIG = {
        "words": "Not the most \\\\ computationally \\\\ efficient",
        "word_height": 4,
    }

    def construct(self):
        big_rect = FullScreenFadeRectangle(opacity=0.5)
        self.add(big_rect)

        words = TextMobject(self.words)
        words.set_color(RED)
        words.set_stroke(WHITE, 1)
        words.scale_to_fit_height(self.word_height)
        self.play(Write(words))
        self.wait()


class SetupSimpleSystemOfEquations(LinearTransformationScene):
    CONFIG = {
        "matrix": [[3, 2], [-1, 2]],
        "output_vect": [-4, -2],
        "quit_before_final_transformation": False,
        "array_scale_factor": 0.75
    }

    def construct(self):
        self.remove_grid()
        self.introduce_system()
        self.from_system_to_matrix()
        self.show_geometry()

    def remove_grid(self):
        self.clear()

    def introduce_system(self):
        system = self.system = self.get_system(self.matrix, self.output_vect)
        big_dim = 7  # Big system size
        big_matrix = np.random.randint(-9, 10, size=(big_dim, big_dim))
        big_output_vect = np.random.randint(-9, 10, size=big_dim)
        big_matrix[:2, :2] = self.matrix
        big_output_vect[:2] = self.output_vect
        big_system = self.get_system(big_matrix, big_output_vect)

        unknown_circles = VGroup(*[
            Circle(color=YELLOW).replace(term).scale(1.5)
            for term in system.unknowns
        ])
        unknown_circles.set_stroke(YELLOW, 2)
        for circle in unknown_circles:
            circle.save_state()
            circle.scale(5)
            circle.fade(1)
        row_rects = VGroup(*map(SurroundingRectangle, system))
        row_rects.set_stroke(BLUE, 2)

        self.add(system)
        self.wait()
        self.play(LaggedStart(
            ApplyMethod, unknown_circles,
            lambda m: (m.restore,),
            lag_ratio=0.7
        ))
        self.play(FadeOut(unknown_circles))
        self.play(LaggedStart(ShowCreation, row_rects, run_time=1, lag_ratio=0.8))
        self.play(FadeOut(row_rects))
        self.wait()
        self.remove(system)
        self.play(ReplacementTransform(system.copy(), big_system))
        self.wait(2)
        # Oh yeah, super readable line...
        self.play(*[
            ReplacementTransform(big_system[i][:5], system[i][:5])
            for i in range(2)
        ] + [
            ReplacementTransform(big_system[i][-2:], system[i][-2:])
            for i in range(2)
        ] + [
            FadeOut(big_system[i][start:end])
            for i in range(big_dim)
            for start in [5 if i < 2 else 0]
            for end in [-2 if i < 2 else len(big_system[i])]
        ])
        self.remove(big_system, system)
        self.add(system)

    def from_system_to_matrix(self):
        system_in_lines = self.system
        matrix_system = self.matrix_system = LinearSystem(
            self.matrix, self.output_vect, height=2
        )
        matrix_system.center()

        corner_rect = self.corner_rect = SurroundingRectangle(
            matrix_system, buff=MED_SMALL_BUFF
        )
        corner_rect.set_stroke(width=0)
        corner_rect.set_fill(BLACK, opacity=0.8)
        corner_rect.scale_to_fit_height(2)
        corner_rect.to_corner(UL, buff=0)

        self.play(system_in_lines.to_edge, UP)
        system_in_lines_copy = system_in_lines.deepcopy()
        self.play(
            ReplacementTransform(
                system_in_lines_copy.matrix_elements,
                matrix_system.matrix_mobject.elements,
            ),
            ReplacementTransform(
                system_in_lines_copy.output_vect_elements,
                matrix_system.output_vect_mob.elements,
            ),
            ReplacementTransform(
                system_in_lines_copy.unknowns[:2],
                matrix_system.input_vect_mob.elements,
            ),
            Write(matrix_system.matrix_mobject.brackets),
            Write(matrix_system.output_vect_mob.brackets),
            Write(matrix_system.input_vect_mob.brackets),
            Write(matrix_system.equals)
        )
        self.wait()
        self.play(
            Write(self.background_plane),
            Write(self.plane),
            FadeOut(system_in_lines),
            FadeIn(corner_rect),
            matrix_system.scale_to_fit_height, corner_rect.get_height() - MED_LARGE_BUFF,
            matrix_system.move_to, corner_rect,
        )
        self.play(*map(GrowArrow, self.basis_vectors))

        self.add_foreground_mobject(corner_rect)
        self.add_foreground_mobject(matrix_system)

    def show_geometry(self):
        system = self.matrix_system
        matrix_mobject = system.matrix_mobject
        columns = VGroup(*[
            VGroup(*matrix_mobject.mob_matrix[:, i])
            for i in 0, 1
        ])

        matrix = np.array(self.matrix)
        first_half_matrix = np.identity(matrix.shape[0])
        first_half_matrix[:, 0] = matrix[:, 0]
        second_half_matrix = np.dot(
            matrix,
            np.linalg.inv(first_half_matrix),
        )

        scale_factor = self.array_scale_factor

        column_mobs = VGroup()
        for i in 0, 1:
            column_mob = IntegerMatrix(matrix[:, i])
            column_mob.elements.set_color([X_COLOR, Y_COLOR][i])
            column_mob.scale(scale_factor)
            column_mob.next_to(self.plane.coords_to_point(*matrix[:, i]), RIGHT)
            column_mob.add_to_back(BackgroundRectangle(column_mob))
            column_mobs.add(column_mob)

        output_vect_mob = self.get_vector(self.output_vect, color=OUTPUT_COLOR)
        output_vect_label = system.output_vect_mob.deepcopy()
        output_vect_label.add_to_back(BackgroundRectangle(output_vect_label))
        output_vect_label.generate_target()
        output_vect_label.target.scale(scale_factor)
        output_vect_label.target.next_to(output_vect_mob.get_end(), LEFT, SMALL_BUFF)

        input_vect = np.dot(np.linalg.inv(self.matrix), self.output_vect)
        input_vect_mob = self.get_vector(input_vect, color=INPUT_COLOR)
        q_marks = TexMobject("????")
        q_marks.set_color_by_gradient(INPUT_COLOR, OUTPUT_COLOR)
        q_marks.next_to(input_vect_mob.get_end(), DOWN, SMALL_BUFF)
        q_marks_rect = SurroundingRectangle(q_marks, color=WHITE)

        # Show output vector
        self.play(
            GrowArrow(output_vect_mob),
            MoveToTarget(output_vect_label),
        )
        self.add_foreground_mobjects(output_vect_mob, output_vect_label)
        self.wait()

        # Show columns
        for column, color in zip(columns, [X_COLOR, Y_COLOR]):
            rect = SurroundingRectangle(column, color=WHITE)
            self.play(
                column.set_color, color,
                system.input_vect_mob.elements.set_color, WHITE,
                ShowPassingFlash(rect),
            )
        matrices = [first_half_matrix, second_half_matrix]
        for column, column_mob, m in zip(columns, column_mobs, matrices):
            column_mob.save_state()
            column_mob[0].scale(0).move_to(matrix_mobject)
            Transform(column_mob.elements, column).update(1)
            Transform(column_mob.brackets, matrix_mobject.brackets).update(1)
            self.add_foreground_mobject(column_mob)
            self.apply_matrix(m, added_anims=[
                ApplyMethod(column_mob.restore, path_arc=90 * DEGREES)
            ])
        self.wait()

        # Do inverse transformation to reveal input
        self.remove_foreground_mobjects(column_mobs)
        self.apply_inverse(self.matrix, run_time=1, added_anims=[
            ReplacementTransform(output_vect_mob.copy(), input_vect_mob),
            ReplacementTransform(output_vect_label.elements.copy(), q_marks),
            FadeOut(column_mobs)
        ])
        self.play(ShowPassingFlash(q_marks_rect))
        self.wait(2)
        if not self.quit_before_final_transformation:
            self.apply_matrix(self.matrix, added_anims=[
                FadeOut(q_marks),
                ReplacementTransform(input_vect_mob, output_vect_mob),
                FadeIn(column_mobs),
            ])
            self.wait()

        self.q_marks = q_marks
        self.input_vect_mob = input_vect_mob
        self.output_vect_mob = output_vect_mob
        self.output_vect_label = output_vect_label
        self.column_mobs = column_mobs

    # Helpers

    def get_system(self, matrix, output_vect):
        if len(matrix) <= 3:
            chars = "xyzwv"
        else:
            chars = ["x_%d" % d for d in range(len(matrix))]
        colors = [
            color
            for i, color in zip(
                range(len(matrix)),
                it.cycle([X_COLOR, Y_COLOR, Z_COLOR, YELLOW, MAROON_B, TEAL])
            )
        ]
        system = VGroup()
        system.matrix_elements = VGroup()
        system.output_vect_elements = VGroup()
        system.unknowns = VGroup()
        for row, num in zip(matrix, output_vect):
            args = []
            for i in range(len(row)):
                if i + 1 == len(row):
                    sign = "="
                elif row[i + 1] < 0:
                    sign = "-"
                else:
                    sign = "+"
                args += [str(abs(row[i])), chars[i], sign]
            args.append(str(num))
            line = TexMobject(*args)
            line.set_color_by_tex_to_color_map(dict([
                (char, color)
                for char, color in zip(chars, colors)
            ]))
            system.add(line)
            system.matrix_elements.add(*line[0:-1:3])
            system.unknowns.add(*line[1:-1:3])
            system.output_vect_elements.add(line[-1])

        system.output_vect_elements.set_color(OUTPUT_COLOR)
        system.arrange_submobjects(
            DOWN,
            buff=0.75,
            index_of_submobject_to_align=-2
        )
        return system


class ShowZeroDeterminantCase(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors": True,
        "matrix": [[3, -2.0], [1, -2.0 / 3]],
        "tex_scale_factor": 1.25,
        "det_eq_symbol": "=",
    }

    def construct(self):
        self.add_equation()
        self.show_det_zero()

    def add_equation(self):
        equation = self.equation = TexMobject(
            "A", "\\vec{\\textbf{x}}", "=", "\\vec{\\textbf{v}}"
        )
        equation.scale(self.tex_scale_factor)
        equation.set_color_by_tex("{x}", INPUT_COLOR)
        equation.set_color_by_tex("{v}", OUTPUT_COLOR)
        equation.add_background_rectangle()
        equation.to_corner(UL)
        self.add(equation)
        self.add_foreground_mobject(equation)

    def show_det_zero(self):
        matrix = self.matrix

        # vect_in_span = [2, 2.0 / 3]
        vect_in_span = [2, 2.0 / 3]
        vect_off_span = [1, 2]
        vect_in_span_mob = self.get_vector(vect_in_span, color=OUTPUT_COLOR)
        vect_off_span_mob = self.get_vector(vect_off_span, color=OUTPUT_COLOR)

        for vect_mob in vect_in_span_mob, vect_off_span_mob:
            circle = Circle(color=WHITE, radius=0.15, stroke_width=2)
            circle.move_to(vect_mob.get_end())
            vect_mob.circle = circle

        vect_off_span_words = TextMobject("No input lands here")
        vect_off_span_words.next_to(vect_off_span_mob.circle, UP)
        vect_off_span_words.add_background_rectangle()

        vect_in_span_words = TextMobject("Many inputs lands here")
        vect_in_span_words.next_to(vect_in_span_mob.circle, DR)
        vect_in_span_words.shift_onto_screen()
        vect_in_span_words.add_background_rectangle()

        moving_group = VGroup(self.plane, self.basis_vectors)
        moving_group.save_state()

        solution = np.dot(np.linalg.pinv(matrix), vect_in_span)
        import sympy
        null_space_basis = np.array(sympy.Matrix(matrix).nullspace())
        null_space_basis = null_space_basis.flatten().astype(float)
        solution_vectors = VGroup(*[
            self.get_vector(
                solution + x * null_space_basis,
                rectangular_stem_width=0.025,
                tip_length=0.2,
            )
            for x in np.linspace(-4, 4, 20)
        ])
        solution_vectors.set_color_by_gradient(YELLOW, MAROON_B)

        self.apply_matrix(matrix, path_arc=0)
        self.wait()
        self.show_det_equation()
        self.wait()

        # Mention zero determinants
        self.play(GrowArrow(vect_off_span_mob))
        self.play(
            ShowCreation(vect_off_span_mob.circle),
            Write(vect_off_span_words),
        )
        self.wait()
        self.play(
            FadeOut(vect_off_span_mob.circle),
            ReplacementTransform(vect_off_span_mob, vect_in_span_mob),
            ReplacementTransform(vect_off_span_words, vect_in_span_words),
            ReplacementTransform(vect_off_span_mob.circle, vect_in_span_mob.circle),
        )
        self.wait(2)
        self.play(
            FadeOut(vect_in_span_words),
            FadeOut(vect_in_span_mob.circle),
            ApplyMethod(moving_group.restore, run_time=2),
            ReplacementTransform(
                VGroup(vect_in_span_mob),
                solution_vectors,
                run_time=2,
            ),
        )
        self.wait()

    # Helpers

    def show_det_equation(self):
        equation = self.equation
        det_equation = TexMobject(
            "\\det(", "A", ")", self.det_eq_symbol, "0"
        )
        det_equation.scale(self.tex_scale_factor)
        det_equation.next_to(equation, DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        det_rect = BackgroundRectangle(det_equation)
        self.play(
            FadeIn(det_rect),
            Write(det_equation[0]),
            ReplacementTransform(
                equation.get_part_by_tex("A").copy(),
                det_equation.get_part_by_tex("A").copy(),
            ),
            Write(det_equation[2:]),
        )
        self.add_foreground_mobject(det_rect, det_equation)


class NonZeroDeterminantCase(ShowZeroDeterminantCase, SetupSimpleSystemOfEquations):
    CONFIG = {
        "det_eq_symbol": "\\neq"
    }

    def construct(self):
        self.add_equation()
        self.show_det_equation()

        output_vect = self.output_vect
        matrix = self.matrix
        input_vect = np.dot(np.linalg.inv(matrix), output_vect)

        input_vect_mob = self.get_vector(input_vect, color=INPUT_COLOR)
        output_vect_mob = self.get_vector(output_vect, color=OUTPUT_COLOR)

        input_vect_label = TextMobject("Input")
        input_vect_label.next_to(input_vect_mob.get_end(), DOWN, SMALL_BUFF)
        input_vect_label.match_color(input_vect_mob)
        output_vect_label = TextMobject("Output")
        output_vect_label.next_to(output_vect_mob.get_end(), DOWN, SMALL_BUFF)
        output_vect_label.match_color(output_vect_mob)
        for label in input_vect_label, output_vect_label:
            label.scale(1.25, about_edge=UP)
            label.add_background_rectangle()

        self.apply_matrix(matrix)
        self.wait()
        self.apply_inverse(matrix)
        self.wait()
        self.play(
            GrowArrow(input_vect_mob),
            Write(input_vect_label),
            run_time=1
        )
        self.wait()
        self.remove(input_vect_mob, input_vect_label)
        self.apply_matrix(matrix, added_anims=[
            ReplacementTransform(input_vect_mob.copy(), output_vect_mob),
            ReplacementTransform(input_vect_label.copy(), output_vect_label),
        ], run_time=2)
        self.wait()
        self.remove(output_vect_mob, output_vect_label)
        self.apply_inverse(matrix, added_anims=[
            ReplacementTransform(output_vect_mob.copy(), input_vect_mob),
            ReplacementTransform(output_vect_label.copy(), input_vect_label),
        ], run_time=2)
        self.wait()


class ThinkOfPuzzleAsLinearCombination(SetupSimpleSystemOfEquations):
    CONFIG = {
        "output_vect": [-4, -2],
    }

    def construct(self):
        self.force_skipping()
        super(ThinkOfPuzzleAsLinearCombination, self).construct()
        self.revert_to_original_skipping_status()

        self.rearrange_equation_as_linear_combination()
        self.show_linear_combination_of_vectors()

    def rearrange_equation_as_linear_combination(self):
        system = self.matrix_system
        corner_rect = self.corner_rect
        matrix, input_vect, equals, output_vect = system

        columns = VGroup(*[
            VGroup(*matrix.mob_matrix[:, i].flatten())
            for i in 0, 1
        ])
        column_arrays = VGroup(*[
            MobjectMatrix(matrix.deepcopy().mob_matrix[:, i])
            for i in 0, 1
        ])
        for column_array in column_arrays:
            column_array.match_height(output_vect)
        x, y = input_vect.elements
        movers = VGroup(x, y, equals, output_vect)
        for mover in movers:
            mover.generate_target()
        plus = TexMobject("+")

        new_system = VGroup(
            x.target, column_arrays[0], plus,
            y.target, column_arrays[1],
            equals.target,
            output_vect.target
        )
        new_system.arrange_submobjects(RIGHT, buff=SMALL_BUFF)
        new_system.move_to(matrix, LEFT)

        corner_rect.generate_target()
        corner_rect.target.stretch_to_fit_width(
            new_system.get_width() + MED_LARGE_BUFF,
            about_edge=LEFT
        )

        self.remove_foreground_mobjects(corner_rect, system)
        self.play(
            MoveToTarget(corner_rect),
            FadeOut(input_vect.brackets),
            ReplacementTransform(matrix.brackets, column_arrays[0].brackets),
            ReplacementTransform(matrix.brackets.copy(), column_arrays[1].brackets),
            ReplacementTransform(columns[0], column_arrays[0].elements),
            ReplacementTransform(columns[1], column_arrays[1].elements),
            Write(plus, rate_func=squish_rate_func(smooth, 0.5, 1)),
            *[
                MoveToTarget(mover, replace_mobject_with_target_in_scene=True)
                for mover in movers
            ],
            path_arc=90 * DEGREES,
            run_time=2
        )
        self.add_foreground_mobject(corner_rect, new_system)
        self.wait()

    def show_linear_combination_of_vectors(self):
        basis_vectors = self.basis_vectors
        input_vect = np.dot(np.linalg.inv(self.matrix), self.output_vect)
        origin = self.plane.coords_to_point(0, 0)
        for basis, scalar in zip(basis_vectors, input_vect):
            basis.ghost = basis.copy()
            basis.ghost.set_color(average_color(basis.get_color(), BLACK))
            self.add_foreground_mobjects(basis.ghost, basis)
            basis.generate_target()
            basis_coords = np.array(self.plane.point_to_coords(basis.get_end()))
            new_coords = scalar * basis_coords
            basis.target.put_start_and_end_on(
                origin, self.plane.coords_to_point(*new_coords),
            )

        dashed_lines = VGroup(*[DashedLine(LEFT, RIGHT) for x in range(2)])

        def update_dashed_lines(lines):
            for i in 0, 1:
                lines[i].put_start_and_end_on(
                    basis_vectors[i].get_start(),
                    basis_vectors[i].get_end(),
                )
                lines[i].shift(basis_vectors[1 - i].get_end() - origin)
            return lines
        update_dashed_lines(dashed_lines)
        self.play(LaggedStart(ShowCreation, dashed_lines, lag_ratio=0.7))
        for basis in basis_vectors:
            self.play(
                MoveToTarget(basis, run_time=2),
                UpdateFromFunc(dashed_lines, update_dashed_lines)
            )
        self.wait()


class WrongButHelpful(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("What's next is wrong, \\\\ but helpful")
        self.change_student_modes("sassy", "sad", "angry")
        self.wait(3)


class LookAtDotProducts(SetupSimpleSystemOfEquations):
    CONFIG = {
        "quit_before_final_transformation": True,
        "equation_scale_factor": 0.7,
    }

    def construct(self):
        self.force_skipping()
        super(LookAtDotProducts, self).construct()
        self.revert_to_original_skipping_status()

        self.remove_corner_system()
        self.show_dot_products()

    def remove_corner_system(self):
        to_remove = [self.corner_rect, self.matrix_system]
        self.remove_foreground_mobjects(*to_remove)
        self.remove(*to_remove)

        q_marks = self.q_marks
        input_vect_mob = self.input_vect_mob

        equations = self.equations = VGroup()
        for i in 0, 1:
            basis = [0, 0]
            basis[i] = 1
            equation = VGroup(
                Matrix(["x", "y"]),
                TexMobject("\\cdot"),
                IntegerMatrix(basis),
                TexMobject("="),
                TexMobject(["x", "y"][i]),
            )
            for part in equation:
                if isinstance(part, Matrix):
                    part.scale(self.array_scale_factor)
            equation[2].elements.set_color([X_COLOR, Y_COLOR][i])
            equation.arrange_submobjects(RIGHT, buff=SMALL_BUFF)
            equation.scale(self.equation_scale_factor)
            equations.add(equation)
        equations.arrange_submobjects(DOWN, buff=MED_LARGE_BUFF)
        equations.to_corner(UL)
        corner_rect = self.corner_rect = BackgroundRectangle(equations, opacity=0.8)
        self.resize_corner_rect_to_mobjet(corner_rect, equations)
        corner_rect.save_state()
        self.resize_corner_rect_to_mobjet(corner_rect, equations[0])

        xy_vect_mob = Matrix(["x", "y"], include_background_rectangle=True)
        xy_vect_mob.scale(self.array_scale_factor)
        xy_vect_mob.next_to(input_vect_mob.get_end(), DOWN, SMALL_BUFF)
        q_marks.add_background_rectangle()
        q_marks.next_to(xy_vect_mob, RIGHT)

        origin = self.plane.coords_to_point(0, 0)
        input_vect_end = input_vect_mob.get_end()
        x_point = (input_vect_end - origin)[0] * RIGHT + origin
        y_point = (input_vect_end - origin)[1] * UP + origin
        v_dashed_line = DashedLine(input_vect_end, x_point)
        h_dashed_line = DashedLine(input_vect_end, y_point)

        h_brace = Brace(Line(x_point, origin), UP, buff=SMALL_BUFF)
        v_brace = Brace(Line(y_point, origin), RIGHT, buff=SMALL_BUFF)

        self.add(xy_vect_mob)
        self.wait()
        self.play(
            FadeIn(corner_rect),
            FadeIn(equations[0][:-1]),
            ShowCreation(v_dashed_line),
            GrowFromCenter(h_brace),
        )
        self.play(
            ReplacementTransform(h_brace.copy(), equations[0][-1])
        )
        self.wait()
        self.play(
            corner_rect.restore,
            Animation(equations[0]),
            FadeIn(equations[1]),
        )
        self.wait()
        self.play(
            ReplacementTransform(equations[1][-1].copy(), v_brace),
            ShowCreation(h_dashed_line),
            GrowFromCenter(v_brace)
        )
        self.wait()

        self.to_fade = VGroup(
            h_dashed_line, v_dashed_line,
            h_brace, v_brace,
            xy_vect_mob, q_marks,
        )

    def show_dot_products(self):
        moving_equations = self.equations.copy()
        transformed_equations = VGroup()
        implications = VGroup()
        transformed_input_rects = VGroup()
        transformed_basis_rects = VGroup()
        for equation in moving_equations:
            equation.generate_target()
            xy_vect, dot, basis, equals, coord = equation.target
            T1, lp1, rp1 = TexMobject("T", "(", ")")
            lp1.scale(1, about_edge=LEFT)
            rp1.scale(1, about_edge=LEFT)
            for paren in lp1, rp1:
                paren.stretch_to_fit_height(equation.get_height())
            T2, lp2, rp2 = T1.copy(), lp1.copy(), rp1.copy()
            transformed_equation = VGroup(
                T1, lp1, xy_vect, rp1, dot,
                T2, lp2, basis, rp2, equals,
                coord
            )
            transformed_equation.arrange_submobjects(RIGHT, buff=SMALL_BUFF)
            # transformed_equation.scale(self.equation_scale_factor)

            implies = TexMobject("\\Rightarrow").scale(1.2)
            implies.next_to(equation, RIGHT)
            implies.set_color(BLUE)

            transformed_equation.next_to(implies, RIGHT)
            implications.add(implies)

            transformed_input_rects.add(SurroundingRectangle(
                transformed_equation[:4],
                color=OUTPUT_COLOR
            ))
            transformed_basis_rects.add(SurroundingRectangle(
                transformed_equation[5:5 + 4],
                color=basis.elements.get_color()
            ))

            for mob in [implies]:
                mob.add(TexMobject("?").next_to(mob, UP, SMALL_BUFF))

            transformed_equation.parts_to_write = VGroup(
                T1, lp1, rp1, T2, lp2, rp2
            )

            transformed_equations.add(transformed_equation)

        corner_rect = self.corner_rect
        corner_rect.generate_target()
        group = VGroup(self.equations, transformed_equations)
        self.resize_corner_rect_to_mobjet(corner_rect.target, group)

        for array in [self.output_vect_label] + list(self.column_mobs):
            array.rect = SurroundingRectangle(array)
            array.rect.match_color(array.elements)

        self.play(
            MoveToTarget(corner_rect),
            Animation(self.equations),
            FadeOut(self.to_fade),
            LaggedStart(Write, implications),
        )
        self.remove(self.input_vect_mob)
        self.apply_matrix(self.matrix, added_anims=[
            Animation(VGroup(corner_rect, self.equations, implications)),
            MoveToTarget(moving_equations[0]),
            LaggedStart(FadeIn, transformed_equations[0].parts_to_write),
            FadeIn(self.column_mobs),
            ReplacementTransform(self.input_vect_mob.copy(), self.output_vect_mob)
        ])
        self.play(
            MoveToTarget(moving_equations[1]),
            LaggedStart(FadeIn, transformed_equations[1].parts_to_write),
            path_arc=-30 * DEGREES,
            run_time=2
        )
        self.wait()

        # Show rectangles
        self.play(
            LaggedStart(ShowCreation, transformed_input_rects, lag_ratio=0.8),
            ShowCreation(self.output_vect_label.rect),
        )
        for tbr, column_mob in zip(transformed_basis_rects, self.column_mobs):
            self.play(
                ShowCreation(tbr),
                ShowCreation(column_mob.rect),
            )
        self.wait()
        self.play(FadeOut(VGroup(
            transformed_input_rects,
            transformed_basis_rects,
            self.output_vect_label.rect,
            *[cm.rect for cm in self.column_mobs]
        )))

        # These computations assume plane is centered at ORIGIN
        output_vect = self.output_vect_mob.get_end()
        c1 = self.basis_vectors[0].get_end()
        c2 = self.basis_vectors[1].get_end()
        x_point = c1 * np.dot(output_vect, c1) / (np.linalg.norm(c1)**2)
        y_point = c2 * np.dot(output_vect, c2) / (np.linalg.norm(c2)**2)

        dashed_line_to_x = DashedLine(self.output_vect_mob.get_end(), x_point)
        dashed_line_to_y = DashedLine(self.output_vect_mob.get_end(), y_point)

        self.play(ShowCreation(dashed_line_to_x))
        self.play(ShowCreation(dashed_line_to_y))
        self.wait()

    # Helpers

    def resize_corner_rect_to_mobjet(self, rect, mobject):
        rect.stretch_to_fit_width(mobject.get_width() + MED_LARGE_BUFF + SMALL_BUFF)
        rect.stretch_to_fit_height(mobject.get_height() + MED_LARGE_BUFF + SMALL_BUFF)
        rect.to_corner(UL, buff=0)
        return rect


class NotAtAllTrue(NotTheMostComputationallyEfficient):
    CONFIG = {
        "words": "Not at all \\\\ True",
        "word_height": 4,
    }


class ShowDotProductChanging(LinearTransformationScene):
    CONFIG = {
        "matrix": [[2, -5.0 / 3], [-5.0 / 3, 2]],
        "v": [1, 2],
        "w": [2, 1],
        "v_label": "v",
        "w_label": "w",
        "v_color": YELLOW,
        "w_color": MAROON_B,
        "rhs1": "> 0",
        "rhs2": "< 0",
        "foreground_plane_kwargs": {
            "x_radius": 2 * FRAME_WIDTH,
            "y_radius": 2 * FRAME_HEIGHT,
        },
        "equation_scale_factor": 1.5,
    }

    def construct(self):
        v_mob = self.add_vector(self.v, self.v_color, animate=False)
        w_mob = self.add_vector(self.w, self.w_color, animate=False)
        kwargs = {
            "transformation_name": "T",
            "at_tip": True,
            "animate": False,
        }
        v_label = self.add_transformable_label(v_mob, self.v_label, **kwargs)
        w_label = self.add_transformable_label(w_mob, self.w_label, **kwargs)

        start_equation = self.get_equation(v_label, w_label, self.rhs1)
        start_equation.to_corner(UR)
        self.play(
            Write(start_equation[0::2]),
            ReplacementTransform(v_label.copy(), start_equation[1]),
            ReplacementTransform(w_label.copy(), start_equation[3]),
        )
        self.wait()
        self.add_foreground_mobject(start_equation)
        self.apply_matrix(self.matrix)
        self.wait()

        end_equation = self.get_equation(v_label, w_label, self.rhs2)
        end_equation.next_to(start_equation, DOWN, aligned_edge=RIGHT)
        self.play(
            FadeIn(end_equation[0]),
            ReplacementTransform(
                start_equation[2::2].copy(),
                end_equation[2::2],
            ),
            ReplacementTransform(v_label.copy(), end_equation[1]),
            ReplacementTransform(w_label.copy(), end_equation[3]),
        )
        self.wait(2)

    def get_equation(self, v_label, w_label, rhs):
        equation = VGroup(
            v_label.copy(),
            TexMobject("\\cdot"),
            w_label.copy(),
            TexMobject(rhs),
        )
        equation.arrange_submobjects(RIGHT, buff=SMALL_BUFF)
        equation.add_to_back(BackgroundRectangle(equation))
        equation.scale(self.equation_scale_factor)
        return equation


class ShowDotProductChangingAwayFromZero(ShowDotProductChanging):
    CONFIG = {
        "matrix": [[2, 2], [0, -1]],
        "v": [1, 0],
        "w": [0, 1],
        "v_label": "x",
        "w_label": "y",
        "v_color": X_COLOR,
        "w_color": Y_COLOR,
        "rhs1": "= 0",
        "rhs2": "\\ne 0",
    }


class OrthonormalWords(Scene):
    def construct(self):
        v_tex = "\\vec{\\textbf{v}}"
        w_tex = "\\vec{\\textbf{w}}"
        top_words = TexMobject(
            "\\text{If }",
            "T(", v_tex, ")", "\\cdot",
            "T(", w_tex, ")", "=",
            v_tex, "\\cdot", w_tex,
            "\\text{ for all }", v_tex, "\\text{ and }", w_tex,
        )
        top_words.set_color_by_tex_to_color_map({
            v_tex: YELLOW,
            w_tex: MAROON_B,
        })
        bottom_words = TextMobject(
            "$T$", "is", "``Orthonormal''"
        )
        bottom_words.set_color_by_tex("Orthonormal", BLUE)
        words = VGroup(top_words, bottom_words)
        words.arrange_submobjects(DOWN, buff=MED_LARGE_BUFF)
        for word in words:
            word.add_background_rectangle()
        words.to_edge(UP)

        self.play(Write(words))
        self.wait()


class ShowSomeOrthonormalTransformations(LinearTransformationScene):
    CONFIG = {
        "random_seed": 1,
        "n_angles": 5
    }

    def construct(self):
        for x in range(self.n_angles):
            angle = TAU * np.random.random() - TAU / 2
            matrix = rotation_matrix(angle, OUT)[:2, :2]
            self.apply_matrix(matrix)


class SolvingASystemWithOrthonormalMatrix(LinearTransformationScene):
    CONFIG = {
        "array_scale_factor": 0.6,
    }

    def construct(self):
        # Setup system
        angle = TAU / 12
        matrix = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)]
        ])
        output_vect = [1, 2]
        symbolic_matrix = [
            ["\\cos(30^\\circ)", "-\\sin(30^\\circ)"],
            ["\\sin(30^\\circ)", "\\cos(30^\\circ)"],
        ]
        system = LinearSystem(
            matrix=symbolic_matrix,
            output_vect=output_vect,
            matrix_config={
                "h_buff": 2.5,
                "element_to_mobject": TexMobject,
            },
            height=1.25,
        )
        system.to_corner(UL)
        system.matrix_mobject.set_color_columns(X_COLOR, Y_COLOR)
        system.input_vect_mob.elements.set_color(WHITE)
        system_rect = BackgroundRectangle(system, buff=MED_SMALL_BUFF)

        matrix_brace = Brace(system.matrix_mobject, DOWN, buff=SMALL_BUFF)
        orthonomal_label = TextMobject("Orthonormal")
        orthonomal_label.set_color(WHITE)
        orthonomal_label.next_to(matrix_brace, DOWN, SMALL_BUFF)
        orthonomal_label.add_background_rectangle()

        # Input and output vectors
        output_vect_mob = self.get_vector(output_vect, color=OUTPUT_COLOR)
        output_vect_label = system.output_vect_mob.copy()
        output_vect_label.add_background_rectangle()
        output_vect_label.scale(self.array_scale_factor)
        output_vect_label.next_to(output_vect_mob.get_end(), RIGHT, buff=SMALL_BUFF)

        input_vect = np.dot(np.linalg.inv(matrix), output_vect)
        input_vect_mob = self.get_vector(input_vect, color=INPUT_COLOR)
        input_vect_label = TextMobject("Mystery input vector")
        input_vect_label.add_background_rectangle()
        input_vect_label.next_to(input_vect_mob.get_end(), RIGHT, SMALL_BUFF)
        input_vect_label.match_color(input_vect_mob)

        # Column arrays
        column_mobs = VGroup()
        for i, vect in zip(range(2), [DR, DL]):
            elements = system.matrix_mobject.deepcopy().mob_matrix[:, i]
            column_mob = MobjectMatrix(elements)
            column_mob.add_background_rectangle()
            column_mob.scale(self.array_scale_factor)
            column_mob.next_to(
                self.get_vector(matrix[:, i]).get_end(), vect,
                buff=SMALL_BUFF
            )
            column_mobs.add(column_mob)
        column_mobs[1].shift(SMALL_BUFF * UP)

        # Dot product lines
        x_point = self.plane.coords_to_point(input_vect[0], 0)
        y_point = self.plane.coords_to_point(0, input_vect[1])
        input_dashed_lines = VGroup(
            DashedLine(input_vect_mob.get_end(), x_point),
            DashedLine(input_vect_mob.get_end(), y_point),
        )
        output_dashed_lines = input_dashed_lines.copy()
        output_dashed_lines.apply_matrix(matrix)

        self.add_foreground_mobjects(system_rect, system)
        self.add_foreground_mobjects(matrix_brace, orthonomal_label)
        self.add_foreground_mobjects(output_vect_mob, output_vect_label)
        self.plane.set_stroke(width=2)

        self.apply_matrix(matrix)
        self.wait()
        self.play(LaggedStart(ShowCreation, output_dashed_lines))
        self.play(*self.get_column_animations(system.matrix_mobject, column_mobs))
        self.wait()
        self.remove(*output_dashed_lines)
        self.apply_inverse(matrix, added_anims=[
            FadeOut(column_mobs),
            ReplacementTransform(output_vect_mob.copy(), input_vect_mob),
            ReplacementTransform(output_dashed_lines.copy(), input_dashed_lines),
            FadeIn(input_vect_label),
        ])
        self.wait()
        self.remove(input_dashed_lines, input_vect_mob)
        self.apply_matrix(matrix, added_anims=[
            FadeOut(input_vect_label),
            ReplacementTransform(input_vect_mob.copy(), output_vect_mob),
            ReplacementTransform(input_dashed_lines.copy(), output_dashed_lines),
            FadeIn(column_mobs),
        ])

        # Write dot product equations
        equations = VGroup()
        for i in 0, 1:
            moving_output_vect_label = output_vect_label.copy()
            moving_column_mob = column_mobs[i].copy()
            moving_var = system.input_vect_mob.elements[i].copy()
            equation = VGroup(
                moving_var.generate_target(),
                TexMobject("="),
                moving_output_vect_label.generate_target(),
                TexMobject("\\cdot"),
                moving_column_mob.generate_target()
            )
            equation.movers = VGroup(moving_var, moving_output_vect_label, moving_column_mob)
            equation.to_write = equation[1::2]
            equation[2].match_height(equation[4])
            equation.arrange_submobjects(RIGHT, buff=SMALL_BUFF)
            equation.background_rectangle = BackgroundRectangle(equation)
            equation.add_to_back(equation.background_rectangle)
            equations.add(equation)
        equations.arrange_submobjects(DOWN, buff=MED_LARGE_BUFF)
        equations.to_corner(UR)

        for i, equation in enumerate(equations):
            self.play(
                FadeIn(equation.background_rectangle),
                Write(equation.to_write),
                LaggedStart(MoveToTarget, equation.movers, path_arc=60 * DEGREES),
            )
            self.wait()

    def get_column_animations(self, matrix_mobject, column_mobs):
        def get_kwargs(i):
            return {
                "rate_func": squish_rate_func(smooth, 0.4 * i, 0.6 + 0.4 * i),
                "run_time": 2,
            }
        return list(it.chain(*[
            [
                FadeIn(cm[0], **get_kwargs(i)),
                ReplacementTransform(
                    matrix_mobject.brackets.copy(),
                    cm.brackets,
                    **get_kwargs(i)
                ),
                ReplacementTransform(
                    VGroup(*matrix_mobject.mob_matrix[:, i]).copy(),
                    cm.elements,
                    **get_kwargs(i)
                ),
            ]
            for i, cm in enumerate(column_mobs)
        ]))
