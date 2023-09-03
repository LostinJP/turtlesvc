![alt text](assets/vcbanner.png)
    
# turtlesvc
Repository for dealtoken distribution dashboard

## Dependencies
dash==2.13.0 </br>
pandas==2.0.3 </br>
plotly==5.16.1 </br>
Requests==2.31.0 </br><br>

Add below 2 environment variables to your ENV file. <br>
SOLSCAN<your key></br>
HELIUS_API=<your key></br>

## How to deploy
Deploy via Amazon Elastic Webstalk service
- Upload with a zip
- Do *not* rename application.py
- After deployment invalidate cache on CloudFront (select your Distribution -> Invalidations -> just select a previous invalidation and hit "Copy to New"


