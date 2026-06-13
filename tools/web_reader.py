import trafilatura

class WebReader:
    def read(self, url: str) -> dict:
        """
        Returns:
        {
            "success": boolean,
            "content": str,
            "title": str | None
        }
        """
        failure_response = {
                "success": False,
                "content": None,
                "title": None,
            }
        downloaded = trafilatura.fetch_url(url)

        if downloaded is None:
            # print(f"Failed to download page: {url}")
            return failure_response

        content = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            output_format="txt",
        )

        if not content:
            # print(f"Failed to extract content: {url}")
            return failure_response
        
        metadata = trafilatura.extract_metadata(downloaded)

        title = None
        if metadata:
            title = metadata.title

        return {
            "success": True,
            "content": content,
            "title": title,
        }