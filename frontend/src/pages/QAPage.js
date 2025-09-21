import React, { useState } from 'react';
import { Button, Input, List, Typography, message } from 'antd';
import axios from 'axios';

const { Title } = Typography;

function QAPage() {
  const [prUrl, setPrUrl] = useState('');
  const [githubToken, setGithubToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [reviewResult, setReviewResult] = useState(null);

  const handleReview = async () => {
    if (!prUrl) {
      message.error('Please enter a PR URL');
      return;
    }
    setLoading(true);
    try {
      const response = await axios.post('/api/v1/pr/review', {
        pr_url: prUrl,
        github_token: githubToken || undefined,
      });
      setReviewResult(response.data);
    } catch (error) {
      message.error(error.response?.data?.detail || 'Error reviewing PR');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <Title level={2}>Pull Request Review</Title>
      <Input
        placeholder="Enter GitHub Pull Request URL"
        value={prUrl}
        onChange={(e) => setPrUrl(e.target.value)}
        style={{ marginBottom: 10 }}
      />
      <Input.Password
        placeholder="Enter GitHub Token (optional)"
        value={githubToken}
        onChange={(e) => setGithubToken(e.target.value)}
        style={{ marginBottom: 10 }}
      />
      <Button type="primary" onClick={handleReview} loading={loading}>
        Review PR
      </Button>

      {reviewResult && (
        <div style={{ marginTop: 20 }}>
          <Title level={4}>Review Summary</Title>
          <p>{reviewResult.message}</p>
          <p>Files Reviewed: {reviewResult.files_reviewed}</p>
          <p>Lines Added: {reviewResult.lines_added}</p>
          {reviewResult.lines_deleted !== undefined && (
            <p>Lines Deleted: {reviewResult.lines_deleted}</p>
          )}
          {reviewResult.suggestions && reviewResult.suggestions.length > 0 && (
            <>
              <Title level={5}>Suggestions</Title>
              <List
                bordered
                dataSource={reviewResult.suggestions}
                renderItem={(item) => <List.Item>{item}</List.Item>}
              />
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default QAPage;