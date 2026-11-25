using UnityEngine;

namespace Skyline
{
    public sealed class BenchmarkOrbit : MonoBehaviour
    {
        private const float Radius = 3.4f;
        private float angle = 32f;

        private void Start()
        {
            MoveCamera();
        }

        private void OnGUI()
        {
            var area = Screen.safeArea;
            var size = Mathf.Clamp(Screen.height * 0.12f, 48f, 128f);
            var y = Screen.height - area.yMin - size - 12f;
            if (GUI.Button(new Rect(area.xMin + 12f, y, size, size), "<"))
            {
                angle -= 15f;
                MoveCamera();
            }

            if (GUI.Button(new Rect(area.xMax - size - 12f, y, size, size), ">"))
            {
                angle += 15f;
                MoveCamera();
            }
        }

        private void MoveCamera()
        {
            var radians = angle * Mathf.Deg2Rad;
            transform.position = new Vector3(Mathf.Sin(radians) * Radius, 1.7f,
                -Mathf.Cos(radians) * Radius);
            transform.LookAt(Vector3.up);
        }
    }
}
