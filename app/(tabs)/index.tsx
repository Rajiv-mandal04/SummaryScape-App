import { useState } from "react";
import {
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";

export default function HomeScreen() {
  const [url, setUrl] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [title, setTitle] = useState("");

  const handleSummarize = async () => {
    if (!url) {
      setSummary("Please paste a YouTube URL");
      return;
    }

    try {
      setLoading(true);
      setSummary("Processing...");
      setTitle("");

      // ✅ Use GET method with query param (matches backend /transcript)
      const backendIP = "192.168.1.69"; // <-- replace with your PC LAN IP
      const response = await fetch(
        `http://${backendIP}:5000/transcript?url=${encodeURIComponent(url)}`
      );

      const data = await response.json();

      if (data.summary) {
        setSummary(data.summary);
        setTitle(data.title || "");
      } else if (data.error) {
        setSummary("Error: " + data.error);
      } else {
        setSummary("No summary found");
      }
    } catch (error) {
      setSummary("Error connecting to backend");
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>🎥 SummaryScape</Text>

      <Text style={styles.subtitle}>
        Paste any YouTube video link and get a quick summary
      </Text>

      <TextInput
        style={styles.input}
        placeholder="Paste YouTube Link..."
        placeholderTextColor="#94a3b8"
        value={url}
        onChangeText={setUrl}
      />

      <TouchableOpacity style={styles.button} onPress={handleSummarize}>
        <Text style={styles.buttonText}>
          {loading ? "Summarizing..." : "Summarize Video"}
        </Text>
      </TouchableOpacity>

      {title ? (
        <Text style={styles.videoTitle}>🎬 {title}</Text>
      ) : null}

      <View style={styles.resultBox}>
        <Text style={styles.resultTitle}>Summary</Text>
        <Text style={styles.resultText}>
          {summary || "Your summary will appear here..."}
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: "#0f172a",
    justifyContent: "center",
    padding: 25,
  },
  title: {
    fontSize: 34,
    fontWeight: "800",
    color: "#fff",
    textAlign: "center",
    marginBottom: 8,
  },
  subtitle: {
    textAlign: "center",
    color: "#94a3b8",
    marginBottom: 25,
    fontSize: 14,
  },
  input: {
    backgroundColor: "#1e293b",
    padding: 16,
    borderRadius: 12,
    color: "white",
    marginBottom: 15,
    borderWidth: 1,
    borderColor: "#334155",
  },
  button: {
    backgroundColor: "#6366f1",
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
    marginBottom: 25,
  },
  buttonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "700",
  },
  videoTitle: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "700",
    marginBottom: 10,
    textAlign: "center",
  },
  resultBox: {
    backgroundColor: "#1e293b",
    padding: 20,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#334155",
  },
  resultTitle: {
    color: "#fff",
    fontWeight: "700",
    marginBottom: 10,
    fontSize: 16,
  },
  resultText: {
    color: "#e2e8f0",
    lineHeight: 22,
    fontSize: 14,
  },
});