using UnityEngine;
using UnityEditor;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.IO;
using System.Collections.Concurrent;
using System;
using System.Collections.Generic;

public class AssetImporterServer : EditorWindow
{
    private static TcpListener listener;
    private static Thread listenerThread;
    private static bool isRunning = false;
    private static string assetsPath = "Assets/ImportedAssets/";
    private static ConcurrentQueue<Action> mainThreadActions = new ConcurrentQueue<Action>();

    [MenuItem("Tools/Asset Importer Server")]
    public static void ShowWindow()
    {
        GetWindow<AssetImporterServer>("Asset Importer Server");
    }

    private void OnGUI()
    {
        if (GUILayout.Button("Start Server"))
        {
            StartServer();
        }

        if (GUILayout.Button("Stop Server"))
        {
            StopServer();
        }

        GUILayout.Label("Server Status: " + (isRunning ? "Running" : "Stopped"));
    }

    private static void StartServer()
    {
        if (isRunning) return;

        if (!Directory.Exists(assetsPath))
        {
            Directory.CreateDirectory(assetsPath);
        }

        listener = new TcpListener(System.Net.IPAddress.Any, 5000);
        listener.Start();
        isRunning = true;

        listenerThread = new Thread(() =>
        {
            while (isRunning)
            {
                try
                {
                    var client = listener.AcceptTcpClient();
                    var stream = client.GetStream();
                    var reader = new StreamReader(stream, Encoding.UTF8);

                    var folderName = reader.ReadLine();
                    var fileName = reader.ReadLine();

                    var textures = new List<Tuple<string, string>>();
                    string line;
                    while ((line = reader.ReadLine()) != null && line.Contains(":"))
                    {
                        var parts = line.Split(new[] { ':' }, 2);
                        textures.Add(new Tuple<string, string>(parts[0], parts[1]));
                    }

                    var fileContentBase64 = line + reader.ReadToEnd();
                    var fileContent = Convert.FromBase64String(fileContentBase64);

                    var folderPath = Path.Combine(assetsPath, folderName);
                    if (!Directory.Exists(folderPath))
                    {
                        Directory.CreateDirectory(folderPath);
                    }

                    var filePath = Path.Combine(folderPath, fileName);
                    File.WriteAllBytes(filePath, fileContent);

                    foreach (var texture in textures)
                    {
                        var texturePath = Path.Combine(folderPath, texture.Item1);
                        var textureContent = Convert.FromBase64String(texture.Item2);
                        File.WriteAllBytes(texturePath, textureContent);
                    }

                    // Enqueue the action to be executed on the main thread
                    mainThreadActions.Enqueue(() =>
                    {
                        AssetDatabase.Refresh();
                        Debug.Log($"Asset and textures imported: {filePath}");
                        CreateAndAssignMaterial(folderName, fileName, folderPath, filePath);
                    });

                    client.Close();
                }
                catch (Exception e)
                {
                    Debug.LogError("Server error: " + e.Message);
                }
            }
        });

        listenerThread.Start();
        EditorApplication.update += MainThreadUpdate;
        Debug.Log("Asset Importer Server started");
    }

    private static void StopServer()
    {
        if (!isRunning) return;

        isRunning = false;
        listener.Stop();
        listenerThread.Abort();
        EditorApplication.update -= MainThreadUpdate;
        Debug.Log("Asset Importer Server stopped");
    }

    private static void MainThreadUpdate()
    {
        while (mainThreadActions.TryDequeue(out var action))
        {
            action();
        }
    }

    private static void CreateAndAssignMaterial(string folderName, string fileName, string folderPath, string assetPath)
    {
        Debug.Log("CreateAndAssignMaterial: Start");
        string materialName = Path.GetFileNameWithoutExtension(fileName);
        if (materialName.StartsWith("SM_"))
        {
            materialName = "M_" + materialName.Substring(3);
        }
        else
        {
            materialName = "M_" + materialName;
        }

        string materialPath = Path.Combine(folderPath, materialName + ".mat");
        Material material = new Material(Shader.Find("Standard"));

        // Assign textures if available
        string baseName = Path.GetFileNameWithoutExtension(fileName);
        string[] textureSuffixes = { "_AlbedoTransparency", "_MetallicSmoothness", "_Normal" };
        string[] textureProperties = { "_MainTex", "_MetallicGlossMap", "_BumpMap" };

        for (int i = 0; i < textureSuffixes.Length; i++)
        {
            string textureName = $"{baseName}{textureSuffixes[i]}.png";
            string texturePath = Path.Combine(folderPath, textureName);
            Debug.Log($"Checking texture path: {texturePath}");
            if (File.Exists(texturePath))
            {
                // Import texture and set import settings for normal map
                var textureImporter = AssetImporter.GetAtPath(texturePath) as TextureImporter;
                if (textureImporter != null)
                {
                    if (textureSuffixes[i] == "_Normal")
                    {
                        textureImporter.textureType = TextureImporterType.NormalMap;
                        textureImporter.SaveAndReimport();
                        Debug.Log($"Marked {textureName} as Normal Map");
                    }
                }

                var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath);
                if (texture != null)
                {
                    material.SetTexture(textureProperties[i], texture);
                    Debug.Log($"Applied texture {textureSuffixes[i]} from: {texturePath} to material {material.name}");
                }
                else
                {
                    Debug.LogWarning($"Failed to load texture from: {texturePath}");
                }
            }
            else
            {
                Debug.LogWarning($"Texture file does not exist: {texturePath}");
            }
        }

        AssetDatabase.CreateAsset(material, materialPath);
        Debug.Log($"Material created: {materialPath}");
        ApplyMaterialToAsset(assetPath, materialPath);
        Debug.Log("CreateAndAssignMaterial: End");

        // Apply any additional textures found in the folder to the material
        ApplyTexturesToMaterial(folderPath, material);
    }

    private static void ApplyMaterialToAsset(string assetPath, string materialPath)
    {
        Debug.Log("ApplyMaterialToAsset: Start");

        GameObject importedAsset = AssetDatabase.LoadAssetAtPath<GameObject>(assetPath);
        if (importedAsset != null)
        {
            Debug.Log($"ApplyMaterialToAsset: Loading material at path {materialPath}");
            Material material = AssetDatabase.LoadAssetAtPath<Material>(materialPath);
            if (material != null)
            {
                Debug.Log("ApplyMaterialToAsset: Applying material to renderers");
                Renderer[] renderers = importedAsset.GetComponentsInChildren<Renderer>();
                foreach (Renderer renderer in renderers)
                {
                    renderer.sharedMaterial = material;
                    Debug.Log($"Applied {material.name} to {renderer.gameObject.name}");
                }
                Debug.Log($"Material {material.name} applied to asset {assetPath}");
            }
            else
            {
                Debug.LogWarning($"Failed to load material: {materialPath}");
            }
        }
        else
        {
            Debug.LogWarning($"Failed to load imported asset: {assetPath}");
        }

        AssetDatabase.SaveAssets();
        Debug.Log("ApplyMaterialToAsset: End");
    }

    private static void ApplyTexturesToMaterial(string folderPath, Material material)
    {
        Debug.Log("ApplyTexturesToMaterial: Start");

        string[] textureSuffixes = { "_AlbedoTransparency", "_MetallicSmoothness", "_Normal" };
        string[] textureProperties = { "_MainTex", "_MetallicGlossMap", "_BumpMap" };

        foreach (var suffix in textureSuffixes)
        {
            string textureName = $"*{suffix}.png"; // Using wildcard to match any file ending with the suffix
            string[] matchingFiles = Directory.GetFiles(folderPath, textureName);
            foreach (var texturePath in matchingFiles)
            {
                Debug.Log($"Checking additional texture path: {texturePath}");
                var textureImporter = AssetImporter.GetAtPath(texturePath) as TextureImporter;
                if (textureImporter != null && suffix == "_Normal")
                {
                    textureImporter.textureType = TextureImporterType.NormalMap;
                    textureImporter.SaveAndReimport();
                    Debug.Log($"Marked {texturePath} as Normal Map");
                }

                var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath);
                if (texture != null)
                {
                    material.SetTexture(textureProperties[Array.IndexOf(textureSuffixes, suffix)], texture);
                    Debug.Log($"Applied additional texture {suffix} from: {texturePath} to material {material.name}");
                }
                else
                {
                    Debug.LogWarning($"Failed to load additional texture from: {texturePath}");
                }
            }
        }

        AssetDatabase.SaveAssets();
        Debug.Log("ApplyTexturesToMaterial: End");
    }

    private void OnDestroy()
    {
        StopServer();
    }
}
