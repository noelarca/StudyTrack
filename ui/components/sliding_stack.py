from PySide6.QtWidgets import QStackedWidget, QGraphicsOpacityEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, Qt

class SlidingStackedWidget(QStackedWidget):
    """
    A QStackedWidget with configurable sliding and fading transition animations.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # --- ADJUSTABLE ANIMATION VALUES ---
        self.duration = 400              # Duration in milliseconds
        self.easing = QEasingCurve.OutCubic # Easing curve (e.g., OutQuad, OutCubic, InOutExpo)
        self.parallax_factor = 0.6       # How much the old widget moves (0.0 to 1.0)
        self.fade_enabled = True         # Toggle fade effect
        # ----------------------------------

        self.m_active = False
        self.m_next_index = -1
        
        # Keep references to animations and effects to prevent garbage collection
        self.anims = []
        self.eff_next = None
        self.eff_curr = None

    def slide_to_index(self, index):
        """
        Slides and fades to the widget at the given index using the configured values.
        """
        if self.currentIndex() == index:
            return
            
        if self.m_active:
            self._stop_animations()

        self.m_active = True
        self.m_next_index = index
        
        direction = 1 if index > self.currentIndex() else -1
        offset = self.width()
        
        if offset <= 0:
            self.setCurrentIndex(index)
            self.m_active = False
            return

        next_widget = self.widget(index)
        curr_widget = self.currentWidget()
        
        # Prepare Next Widget
        next_widget.setGeometry(0, 0, self.width(), self.height())
        next_widget.setAttribute(Qt.WA_TranslucentBackground) # Hint for smoother blending
        next_widget.move(direction * offset, 0)
        next_widget.show()
        next_widget.raise_()
        
        if self.fade_enabled:
            self.eff_next = QGraphicsOpacityEffect(next_widget)
            # Enable hardware acceleration for the effect
            self.eff_next.setEnabled(True)
            next_widget.setGraphicsEffect(self.eff_next)
            self.eff_next.setOpacity(0.0)
        
        # 2. Prepare Current Widget
        if self.fade_enabled:
            self.eff_curr = QGraphicsOpacityEffect(curr_widget)
            self.eff_curr.setEnabled(True)
            curr_widget.setGraphicsEffect(self.eff_curr)
            self.eff_curr.setOpacity(1.0)
        
        # 3. Create Animations
        self.anims = []
        
        # Slide Next (Into view)
        anim_next_pos = QPropertyAnimation(next_widget, b"pos", self)
        anim_next_pos.setDuration(self.duration)
        anim_next_pos.setEasingCurve(self.easing)
        anim_next_pos.setStartValue(QPoint(direction * offset, 0))
        anim_next_pos.setEndValue(QPoint(0, 0))
        self.anims.append(anim_next_pos)
        
        # Slide Current (Out of view with parallax)
        anim_curr_pos = QPropertyAnimation(curr_widget, b"pos", self)
        anim_curr_pos.setDuration(self.duration)
        anim_curr_pos.setEasingCurve(self.easing)
        anim_curr_pos.setStartValue(QPoint(0, 0))
        anim_curr_pos.setEndValue(QPoint(int(-direction * offset * self.parallax_factor), 0))
        self.anims.append(anim_curr_pos)
        
        if self.fade_enabled:
            # Fade In Next
            anim_next_fade = QPropertyAnimation(self.eff_next, b"opacity", self)
            anim_next_fade.setDuration(self.duration)
            anim_next_fade.setStartValue(0.0)
            anim_next_fade.setEndValue(1.0)
            self.anims.append(anim_next_fade)
            
            # Fade Out Current
            anim_curr_fade = QPropertyAnimation(self.eff_curr, b"opacity", self)
            anim_curr_fade.setDuration(self.duration)
            anim_curr_fade.setStartValue(1.0)
            anim_curr_fade.setEndValue(0.0)
            self.anims.append(anim_curr_fade)
        
        # Connect the finished signal to cleanup
        anim_next_pos.finished.connect(self._on_animation_finished)
        
        # Start all animations
        for anim in self.anims:
            anim.start()

    def _stop_animations(self):
        for anim in self.anims:
            anim.stop()
        self._on_animation_finished()

    def _on_animation_finished(self):
        """
        Cleanup after animation ends.
        """
        if self.m_next_index != -1:
            self.setCurrentIndex(self.m_next_index)
            
            # Reset all widgets position and remove effects
            for i in range(self.count()):
                w = self.widget(i)
                w.move(0, 0)
                w.setGraphicsEffect(None)
                if i != self.currentIndex():
                    w.hide()
            
            self.m_next_index = -1
        
        self.m_active = False
        self.anims = []
        self.eff_next = None
        self.eff_curr = None

    def resizeEvent(self, event):
        if self.currentWidget():
            self.currentWidget().setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)
