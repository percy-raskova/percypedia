---
category: Methods
Confidence: high
Date: '2024-11-10'
Implementation: MCP servers for federal APIs
Related: '{doc}`/concepts/lumpen_organizing`, {doc}`/concepts/dialectical_materialism`'
Status: active-development
Tags: organizing, data, methodology, praxis
Updated: '2024-11-26'
---

# SICA Methodology


## Overview

{term}`SICA` (Social Investigation and Class Analysis) is a data-driven methodology
for material analysis at granular geographic levels. It uses publicly-accessible
federal APIs to gather concrete data about {term}`material conditions` rather than
relying on abstract theoretical frameworks.

:::{important}
SICA isn't just research—it's organizing infrastructure. Data becomes basis for
strategic decisions, resource allocation, and coalition building.
:::

## Theoretical Foundation

### Mao's Social Investigation

```{eval-rst}
.. epigraph::

   "No investigation, no right to speak."

   -- Mao Zedong, *Oppose Book Worship* (1930)
```

Mao emphasized concrete investigation of actual conditions over theoretical
abstraction. SICA applies this principle using modern data infrastructure.

**Mao's approach**:

1. Go to the field
2. Conduct interviews, surveys
3. Gather material data (land ownership, crop yields, debt levels)
4. Analyze class structure from material relations
5. Develop strategy based on findings

**SICA adaptation**:

1. Identify geographic area (ZIP code, census tract)
2. Query federal APIs (Census, BLS, HUD, etc.)
3. Gather material data (income, employment, housing, incarceration)
4. Analyze class composition from aggregate statistics
5. Develop organizing strategy based on findings

### Grounded in Dialectical Materialism

SICA implements {term}`dialectical materialism` (see {doc}`/concepts/dialectical_materialism`)
by starting with {term}`material conditions`:

```text
Traditional Leftist Approach:
Theory → Strategy → Investigation (if at all)

SICA Approach:
Investigation → Material Analysis → Strategy → Theory

Result: Strategy grounded in actual conditions, not ideology
```

This is *materialist* methodology—let data shape theory, not vice versa.

## Why Federal APIs?

### Accessibility

Federal data is:

- **Publicly accessible**: No special credentials required
- **Legally mandated**: Government obligated to provide it
- **Comprehensive**: Decades of collected data
- **Granular**: Often down to census tract or block group
- **Free**: Taxpayer-funded, no cost to access

This democratizes material analysis—no need for university affiliation or
institutional resources.

:::{note}
While corporations and law enforcement have more detailed data, federal APIs
provide sufficient granularity for organizing decisions. Perfect is enemy of
good enough.
:::

### Available Data Sources

```{eval-rst}
.. table:: Key Federal APIs for SICA
   :widths: 25 40 35

   ===================  =============================  ==========================
   Agency               Data Available                 Organizing Application
   ===================  =============================  ==========================
   Census Bureau        Income, poverty, demographics  Class composition
   BLS                  Employment, unemployment       Economic conditions
   HUD                  Housing costs, homelessness    Material deprivation
   DOJ/BJS              Incarceration rates            Lumpen concentration
   CDC                  Health outcomes, mortality     Quality of life
   FBI UCR              Crime statistics               State violence patterns
   USDA                 Food insecurity                Basic needs metrics
   ===================  =============================  ==========================
```

### MCP Server Implementation

Model Context Protocol (MCP) servers provide interface to federal APIs:

```python
# Example: MCP server for Census API

from mcp import MCPServer, Tool

class CensusAPIServer(MCPServer):
    """MCP server for Census Bureau API"""

    @Tool(
        name="get_poverty_rate",
        description="Get poverty rate for ZIP code or census tract"
    )
    async def get_poverty_rate(self, geographic_id: str) -> dict:
        """Query Census API for poverty statistics"""
        url = f"https://api.census.gov/data/2022/acs/acs5"
        params = {
            'get': 'B17001_001E,B17001_002E',  # Total pop, below poverty
            'for': f'zip code tabulation area:{geographic_id}',
            'key': self.api_key
        }

        response = await self.http_client.get(url, params=params)
        data = response.json()

        total_pop = int(data[1][0])
        below_poverty = int(data[1][1])
        poverty_rate = (below_poverty / total_pop) * 100

        return {
            'geographic_id': geographic_id,
            'total_population': total_pop,
            'below_poverty': below_poverty,
            'poverty_rate': poverty_rate,
            'data_year': 2022,
            'source': 'Census Bureau ACS 5-year estimates'
        }
```

See `github.com/percy/mcp-federal-apis` for complete implementation (fictional
example path).

## Practical Application

### Step 1: Define Geographic Scope

Start with manageable area:

- **Too broad**: Entire city → averages obscure variation
- **Too narrow**: Single block → not enough data, privacy concerns
- **Optimal**: ZIP code or census tract → balance of granularity and data availability

```python
# Example: Identifying organizing targets in Maryland

maryland_zips = [
    '21201',  # Baltimore downtown
    '21217',  # West Baltimore
    '20910',  # Silver Spring
    '20783',  # Hyattsville
]

for zip_code in maryland_zips:
    profile = generate_sica_profile(zip_code)
    if profile['lumpen_concentration'] > 0.6:
        priority_areas.append(zip_code)
```

### Step 2: Gather Core Metrics

Essential data points for {term}`lumpen` organizing (see {doc}`/concepts/lumpen_organizing`):

```python
def generate_sica_profile(zip_code: str) -> dict:
    """Generate comprehensive SICA profile for area"""

    # Economic metrics
    median_income = census.get_median_income(zip_code)
    poverty_rate = census.get_poverty_rate(zip_code)
    unemployment = bls.get_unemployment_rate(zip_code)

    # Housing metrics
    median_rent = census.get_median_rent(zip_code)
    rent_burden = calculate_rent_burden(median_rent, median_income)
    eviction_rate = hud.get_eviction_rate(zip_code)

    # Criminalization metrics
    incarceration_rate = bjs.get_incarceration_rate(zip_code)
    arrest_rate = fbi_ucr.get_arrest_rate(zip_code)

    # Health/quality of life
    life_expectancy = cdc.get_life_expectancy(zip_code)
    uninsured_rate = census.get_uninsured_rate(zip_code)

    # Calculate composite scores
    lumpen_index = calculate_lumpen_concentration({
        'poverty': poverty_rate,
        'unemployment': unemployment,
        'incarceration': incarceration_rate,
        'rent_burden': rent_burden
    })

    labor_aristocracy_index = calculate_labor_aristocracy({
        'income': median_income,
        'homeownership': census.get_homeownership_rate(zip_code),
        'education': census.get_bachelors_rate(zip_code)
    })

    return {
        'zip_code': zip_code,
        'median_income': median_income,
        'poverty_rate': poverty_rate,
        'unemployment': unemployment,
        'incarceration_rate': incarceration_rate,
        'lumpen_index': lumpen_index,
        'labor_aristocracy_index': labor_aristocracy_index,
        'organizing_priority': prioritize(lumpen_index, labor_aristocracy_index)
    }
```

### Step 3: Analyze Class Composition

Use data to understand class structure:

```text
Example: ZIP 21217 (West Baltimore)

Median Income: $32,000 (vs. national $70,000)
Poverty Rate: 38% (vs. national 12%)
Unemployment: 14% (vs. national 4%)
Incarceration Rate: 4.2% adult population

Analysis:
→ High lumpen concentration (lumpen_index: 0.78)
→ Low labor aristocracy (la_index: 0.15)
→ Organizing Priority: HIGH

Strategy: Focus on:
- Returning citizens (high incarceration rate)
- Material support (high poverty/unemployment)
- Avoiding union entryism (low traditional employment)
```

### Step 4: Develop Strategy

Data informs organizing approach:

**High lumpen / Low labor aristocracy** (like example above):

- Independent organization, not entryism
- Material support networks critical
- Legal support for criminalized populations
- Build alternatives to state provision

**Mixed composition**:

- Identify specific neighborhoods within ZIP
- Different approaches for different areas
- Coalition building between fractions

**High labor aristocracy / Low lumpen**:

- Likely low organizing priority
- If organizing here, expect reformist politics
- Focus on solidarity actions, not revolutionary base

## Comparison to Traditional Methods

```{eval-rst}
.. table:: SICA vs. Traditional Organizing
   :widths: 30 35 35

   =======================  ========================  ======================
   Aspect                   Traditional Left          SICA Methodology
   =======================  ========================  ======================
   Starting point           Theory, ideology          Material data
   Geographic targeting     Intuition, convenience    Data-driven priorities
   Class analysis           Abstract categories       Concrete metrics
   Resource allocation      Political preferences     Strategic optimization
   Evaluation               Vibes, attendance         Measurable outcomes
   =======================  ========================  ======================
```

**Traditional approach problems**:

- Organizers work where they live (often not highest-priority areas)
- Strategy based on what *should* work per theory
- No systematic evaluation of outcomes
- Arguments over ideology substitute for material analysis

**SICA advantages**:

- Objective prioritization of organizing targets
- Strategy grounded in actual conditions
- Measurable metrics for evaluation
- Data settles debates about material reality

:::{note}
SICA doesn't replace political judgment—it informs it. Data shows *what is*,
organizers decide *what to do*.
:::

## Technical Infrastructure

### Data Collection Pipeline

```python
# Automated SICA data collection

import asyncio
from typing import List

class SICADataCollector:
    """Orchestrate data collection from multiple APIs"""

    def __init__(self):
        self.census = CensusAPIServer()
        self.bls = BLSAPIServer()
        self.hud = HUDAPIServer()
        self.bjs = BJSAPIServer()

    async def collect_area_profile(
        self,
        zip_codes: List[str]
    ) -> List[dict]:
        """Collect comprehensive profiles for multiple areas"""
        tasks = [
            self.generate_profile(zip_code)
            for zip_code in zip_codes
        ]
        return await asyncio.gather(*tasks)

    async def generate_profile(self, zip_code: str) -> dict:
        """Generate profile for single area (parallel API calls)"""
        results = await asyncio.gather(
            self.census.get_poverty_rate(zip_code),
            self.census.get_median_income(zip_code),
            self.bls.get_unemployment_rate(zip_code),
            self.census.get_demographics(zip_code),
            self.hud.get_housing_metrics(zip_code),
            self.bjs.get_incarceration_rate(zip_code),
        )

        return self.synthesize_profile(zip_code, results)
```

### Storage and Versioning

Track data over time to identify trends:

```sql
-- PostgreSQL schema for SICA data

CREATE TABLE sica_profiles (
    id SERIAL PRIMARY KEY,
    zip_code VARCHAR(5) NOT NULL,
    collection_date DATE NOT NULL,

    -- Economic metrics
    median_income INTEGER,
    poverty_rate DECIMAL(5,2),
    unemployment_rate DECIMAL(5,2),

    -- Housing metrics
    median_rent INTEGER,
    rent_burden DECIMAL(5,2),
    eviction_rate DECIMAL(5,2),

    -- Criminalization metrics
    incarceration_rate DECIMAL(5,2),
    arrest_rate DECIMAL(5,2),

    -- Derived indices
    lumpen_index DECIMAL(5,3),
    labor_aristocracy_index DECIMAL(5,3),
    organizing_priority VARCHAR(10),

    -- Metadata
    data_sources JSONB,
    notes TEXT,

    UNIQUE(zip_code, collection_date)
);

-- Index for time-series queries
CREATE INDEX idx_sica_timeseries
ON sica_profiles(zip_code, collection_date);
```

This enables longitudinal analysis: How is area changing? Are conditions
deteriorating (increasing lumpen concentration)? Improving (gentrification)?

### Visualization

Make data accessible to organizers without technical background:

```python
def generate_organizing_map(region: str) -> str:
    """Generate interactive map of organizing priorities"""

    profiles = db.query_recent_profiles(region)

    # Create choropleth map colored by lumpen_index
    map_data = {
        'type': 'FeatureCollection',
        'features': []
    }

    for profile in profiles:
        feature = {
            'type': 'Feature',
            'geometry': get_zip_geometry(profile.zip_code),
            'properties': {
                'zip_code': profile.zip_code,
                'lumpen_index': profile.lumpen_index,
                'priority': profile.organizing_priority,
                'popup': generate_popup_html(profile)
            }
        }
        map_data['features'].append(feature)

    return render_leaflet_map(map_data)
```

## Security Considerations

### API Keys and Rate Limits

Most federal APIs require keys but are free:

```bash
# Store keys securely
export CENSUS_API_KEY="your_key_here"
export BLS_API_KEY="your_key_here"

# Use age encryption for config files
age -e -i ~/.ssh/id_ed25519 sica_config.json > sica_config.json.age
```

**Rate limiting**:

- Census API: 500 requests/day (IP-based)
- BLS API: Similar limits
- Solution: Cache aggressively, data doesn't change daily

### OPSEC for Organizing

:::{warning}
**Threat model**: State monitors organizing activity. SICA data collection
itself isn't illegal, but combined with organizing creates profile.
:::

**Mitigation**:

1. **VPN/Tor for API queries**: Don't link organizing location to data queries
2. **Aggregate before sharing**: Share analysis, not raw query patterns
3. **Local caching**: Minimize repeated queries that create patterns
4. **Compartmentalization**: Separate data analysis from direct organizing work

See {doc}`/systems/druids_architecture` for secure information sharing.

## Limitations and Critiques

### What SICA Cannot Do

❌ **Replace political theory**: Data shows conditions, not path forward

❌ **Substitute for relationships**: Numbers don't build trust with communities

❌ **Determine tactics**: Strategy informed by data, tactics from local context

❌ **Capture everything**: Undocumented populations, informal economies underrepresented

### What SICA Does Well

✓ **Objective prioritization**: Evidence-based allocation of limited resources

✓ **Hypothesis testing**: Validate assumptions about class composition

✓ **Longitudinal tracking**: Monitor changing conditions over time

✓ **Common ground**: Data settles factual disputes, focuses debates on strategy

### Critique from Orthodox Marxism

**Objection**: "This is empiricism, not Marxism. You can't reduce class to statistics."

**Response**: SICA uses data to *measure* material conditions, not *define* class.
Class is still relational (relationship to means of production). Data helps us
*locate* class fractions geographically. This is materialism, not empiricism.

**Objection**: "Organizing should be where workers are conscious, not where data says."

**Response**: This is idealism—prioritizing consciousness over material base.
{term}`Dialectical materialism` says investigate material conditions first. See
{doc}`/concepts/dialectical_materialism`.

## Connections

**Theoretical Grounding**:

- {doc}`/concepts/dialectical_materialism` - Materialist methodology
- {doc}`/concepts/lumpen_organizing` - Who to organize with SICA data

**System Implementation**:

- {doc}`/systems/druids_architecture` - Secure data infrastructure
- {doc}`/concepts/desire_paths` - Let data reveal patterns organically

**Practical Work**:

- {term}`praxis` - Investigation informs action, action informs investigation
- {term}`material conditions` - What SICA measures

## Further Reading

### Theoretical

- Mao Zedong. *Oppose Book Worship* (1930)
- Mao Zedong. *Report on an Investigation of the Peasant Movement in Hunan* (1927)
- Fanon, Frantz. *The Wretched of the Earth* (1961) - Ch. 1 on lumpen analysis

### Technical

- Census Bureau API documentation: <https://www.census.gov/data/developers.html>
- Bureau of Labor Statistics API: <https://www.bls.gov/developers/>
- Model Context Protocol spec: <https://modelcontextprotocol.io>

:::{note}
SICA represents synthesis: Maoist investigation principles + modern data
infrastructure. Neither is sufficient alone—investigation without data is
anecdotal, data without investigation is technocratic. Together: {term}`praxis`.
:::
