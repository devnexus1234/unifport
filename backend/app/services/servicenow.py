import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging_config import get_logger
import logging
import xml.etree.ElementTree as ET

logger = get_logger(__name__)

class ServiceNowClient:
    def __init__(self):
        self.base_url = settings.SNOW_API_URL
        self.user = settings.SNOW_USER
        self.password = settings.SNOW_PASSWORD
        self.timeout = 30.0
        
    def _get_auth(self):
        if not self.user or not self.password:
            return None
        return (self.user, self.password)

    async def fetch_table_data(
        self, 
        table: str, 
        query: Optional[str] = None, 
        page_size: int = 1000, 
        max_pages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch data from a ServiceNow table with pagination support.
        
        Args:
            table: The table name to fetch from (e.g., 'cmdb_ci_ip_network')
            query: Optional sysparm_query
            page_size: Number of records per page (sysparm_limit)
            max_pages: Maximum number of pages to fetch. If None, fetch all.
        """
        if not self.base_url:
            logger.warning("ServiceNow API URL not configured. Returning empty list.")
            return []

        # Construct base URL for the table
        # If base_url already contains /api/now/table, we assume it's the root.
        # But usually SNOW_API_URL in config might be just instance URL or table API root.
        # Let's handle both cases gracefully-ish or just assume config is root of Table API.
        # Given previous usage was `url = self.base_url`, let's assume base_url is `.../api/now/table`.
        # So we append /{table}.
        
        base_api_url = self.base_url.rstrip('/')
        url = f"{base_api_url}/{table}"
        
        all_records = []
        offset = 0
        pages_fetched = 0
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while True:
                if max_pages and pages_fetched >= max_pages:
                    logger.info(f"Reached max pages limit ({max_pages}). Stopping fetch.")
                    break
                
                params = {
                    "sysparm_limit": page_size,
                    "sysparm_offset": offset,
                    "sysparm_exclude_reference_link": "true"
                }
                if query:
                    params["sysparm_query"] = query

                logger.info(f"Fetching {table} (Offset: {offset}, Limit: {page_size})")

                try:
                    response = await client.get(
                        url, 
                        auth=self._get_auth(),
                        headers={"Accept": "application/xml"}, # Request XML per user requirement
                        params=params
                    )
                    response.raise_for_status()
                    
                    # Parse XML response
                    # Expected format: <response><result><tablename>...</tablename>...</result></response>
                    root = ET.fromstring(response.text)
                    
                    # Find all records inside result
                    # Using match to find direct children of result is safer, but .//result/* works too
                    # Usually response > result > [table_name_elements]
                    
                    # Check if result exists
                    result_node = root.find("result")
                    if result_node is None:
                        logger.warning("No result node found in XML response")
                        break
                        
                    batch_records = []
                    for record_node in result_node:
                        record_dict = {}
                        for field in record_node:
                            record_dict[field.tag] = field.text
                        batch_records.append(record_dict)
                    
                    if not batch_records:
                        break
                        
                    all_records.extend(batch_records)
                    
                    # If we got fewer records than page_size, we are done
                    if len(batch_records) < page_size:
                        break
                        
                    offset += page_size
                    pages_fetched += 1
                    
                except httpx.HTTPStatusError as e:
                    logger.error(f"ServiceNow API error fetching {table}: {e.response.status_code} - {e.response.text}")
                    raise
                except ET.ParseError as e:
                    logger.error(f"Failed to parse XML response from ServiceNow: {e}")
                    raise
                except Exception as e:
                    logger.error(f"Failed to fetch from ServiceNow ({table}): {str(e)}")
                    raise
                    
        return all_records

snow_client = ServiceNowClient()
